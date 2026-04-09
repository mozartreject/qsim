"""
QSIM Gateway — FastAPI Telemetry Ingestion Service
Receives factory asset telemetry, validates, stores, and exposes metrics.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
import json
import os
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("qsim-gateway")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="QSIM Gateway",
    description="Quantum-Safe Industrial Mesh — Telemetry Ingestion API",
    version="1.0.0"
)

# ── Persistent storage path (mounted via PVC in Kubernetes) ───────────────────
DATA_DIR = os.getenv("DATA_DIR", "/data")
LOG_FILE = os.path.join(DATA_DIR, "telemetry.jsonl")
os.makedirs(DATA_DIR, exist_ok=True)

# ── Prometheus Metrics ────────────────────────────────────────────────────────
TELEMETRY_RECEIVED   = Counter("qsim_telemetry_received_total", "Total telemetry payloads received", ["asset_id", "status"])
TELEMETRY_LATENCY    = Histogram("qsim_telemetry_processing_seconds", "Telemetry processing latency")
ACTIVE_ASSETS        = Gauge("qsim_active_assets", "Number of unique assets seen")
TEMPERATURE_GAUGE    = Gauge("qsim_asset_temperature_celsius", "Last reported temperature", ["asset_id"])
VIBRATION_GAUGE      = Gauge("qsim_asset_vibration", "Last reported vibration", ["asset_id"])
HEALTH_SCORE_GAUGE   = Gauge("qsim_asset_health_score", "Last reported health score", ["asset_id"])

# ── In-memory asset registry ──────────────────────────────────────────────────
asset_registry: dict = {}

# ── Pydantic Models ───────────────────────────────────────────────────────────
class TelemetryPayload(BaseModel):
    asset_id: str = Field(..., min_length=1, max_length=64, description="Unique asset identifier")
    asset_type: Literal["CNC_MACHINE", "CONVEYOR", "ROBOT_ARM", "SENSOR", "PRESS"] = Field(..., description="Type of factory asset")
    temperature: float = Field(..., ge=-50.0, le=500.0, description="Temperature in Celsius")
    vibration: float = Field(..., ge=0.0, le=100.0, description="Vibration level 0–100")
    health_score: float = Field(..., ge=0.0, le=1.0, description="Health score 0.0–1.0")
    operational_state: Literal["RUNNING", "IDLE", "FAULT", "MAINTENANCE"] = Field(...)
    metadata: Optional[dict] = Field(default={}, description="Optional extra fields")

    @validator("asset_id")
    def sanitize_asset_id(cls, v):
        # Prevent path traversal or injection in asset_id
        return v.strip().replace("/", "_").replace("..", "_")

class TelemetryResponse(BaseModel):
    status: str
    asset_id: str
    ingested_at: str
    record_id: int

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    total_records: int
    unique_assets: int

# ── Startup time ──────────────────────────────────────────────────────────────
START_TIME = time.time()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Operations"])
def health_check():
    """Kubernetes liveness + readiness probe endpoint."""
    try:
        record_count = 0
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                record_count = sum(1 for _ in f)
        return {
            "status": "healthy",
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "total_records": record_count,
            "unique_assets": len(asset_registry)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service degraded")

@app.get("/ready", tags=["Operations"])
def readiness_check():
    """Readiness probe — confirms data directory is writable."""
    try:
        test_file = os.path.join(DATA_DIR, ".ready")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Storage not ready")

@app.post("/ingest", response_model=TelemetryResponse, tags=["Telemetry"])
def ingest_telemetry(payload: TelemetryPayload):
    """
    Primary telemetry ingestion endpoint.
    Validates payload, persists to JSONL log, updates Prometheus metrics.
    """
    start = time.time()
    try:
        ingested_at = datetime.utcnow().isoformat() + "Z"

        # Build record
        record = {
            "ingested_at": ingested_at,
            **payload.dict()
        }

        # Persist to JSONL (append-only, survives pod restarts via PVC)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")

        # Count lines for record_id
        with open(LOG_FILE, "r") as f:
            record_id = sum(1 for _ in f)

        # Update asset registry
        asset_registry[payload.asset_id] = {
            "last_seen": ingested_at,
            "state": payload.operational_state
        }

        # Update Prometheus metrics
        TELEMETRY_RECEIVED.labels(asset_id=payload.asset_id, status="success").inc()
        TEMPERATURE_GAUGE.labels(asset_id=payload.asset_id).set(payload.temperature)
        VIBRATION_GAUGE.labels(asset_id=payload.asset_id).set(payload.vibration)
        HEALTH_SCORE_GAUGE.labels(asset_id=payload.asset_id).set(payload.health_score)
        ACTIVE_ASSETS.set(len(asset_registry))

        logger.info(f"Ingested telemetry from {payload.asset_id} state={payload.operational_state}")

        return {
            "status": "ingested",
            "asset_id": payload.asset_id,
            "ingested_at": ingested_at,
            "record_id": record_id
        }

    except Exception as e:
        TELEMETRY_RECEIVED.labels(asset_id=payload.asset_id, status="error").inc()
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        TELEMETRY_LATENCY.observe(time.time() - start)

@app.get("/assets", tags=["Digital Twin"])
def list_assets():
    """Returns all known assets and their last seen state."""
    return {"assets": asset_registry, "count": len(asset_registry)}

@app.get("/assets/{asset_id}", tags=["Digital Twin"])
def get_asset(asset_id: str):
    """Returns the last known state of a specific asset."""
    if asset_id not in asset_registry:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return {"asset_id": asset_id, **asset_registry[asset_id]}

@app.get("/telemetry", tags=["Digital Twin"])
def get_recent_telemetry(limit: int = 50):
    """Returns the last N telemetry records from persistent storage."""
    try:
        if not os.path.exists(LOG_FILE):
            return {"records": [], "count": 0}
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        records = [json.loads(l) for l in lines[-limit:]]
        return {"records": records, "count": len(records)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", tags=["Operations"])
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/", tags=["Operations"])
def root():
    return {
        "system": "QSIM — Quantum-Safe Industrial Mesh",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": ["/ingest", "/assets", "/telemetry", "/health", "/metrics"]
    }
