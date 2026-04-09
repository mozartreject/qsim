"""
QSIM Factory Generator — Simulates factory asset telemetry
Sends randomized sensor data to the QSIM Gateway via HTTP POST
"""

import httpx
import random
import time
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("factory-gen")

# ── Config ────────────────────────────────────────────────────────────────────
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://qsim-gateway-svc/ingest")
INTERVAL    = float(os.getenv("SEND_INTERVAL", "2.0"))   # seconds between sends
NUM_ASSETS  = int(os.getenv("NUM_ASSETS", "5"))

ASSET_TYPES = ["CNC_MACHINE", "CONVEYOR", "ROBOT_ARM", "SENSOR", "PRESS"]
STATES      = ["RUNNING", "IDLE", "FAULT", "MAINTENANCE"]

# Simulate realistic asset profiles
ASSETS = [
    {"id": f"ASSET-{str(i+1).zfill(3)}", "type": ASSET_TYPES[i % len(ASSET_TYPES)]}
    for i in range(NUM_ASSETS)
]

def generate_telemetry(asset: dict) -> dict:
    """Generate realistic-looking telemetry for an asset."""
    # Occasionally inject fault states for chaos demo realism
    state_weights = [0.70, 0.20, 0.05, 0.05]
    state = random.choices(STATES, weights=state_weights)[0]

    # Temperature varies by state
    base_temp = 65.0 if state == "RUNNING" else 30.0
    temperature = round(base_temp + random.uniform(-5, 15), 2)

    # Vibration spikes on fault
    vibration = round(random.uniform(60, 90) if state == "FAULT" else random.uniform(5, 35), 2)

    # Health degrades on fault/maintenance
    health = round(random.uniform(0.3, 0.6) if state in ["FAULT", "MAINTENANCE"] else random.uniform(0.75, 1.0), 3)

    return {
        "asset_id": asset["id"],
        "asset_type": asset["type"],
        "temperature": temperature,
        "vibration": vibration,
        "health_score": health,
        "operational_state": state,
        "metadata": {
            "generator_ts": datetime.utcnow().isoformat() + "Z",
            "simulation": True
        }
    }

def run():
    logger.info(f"QSIM Factory Generator starting — {NUM_ASSETS} assets → {GATEWAY_URL}")
    client = httpx.Client(timeout=10.0)

    while True:
        for asset in ASSETS:
            payload = generate_telemetry(asset)
            try:
                resp = client.post(GATEWAY_URL, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"✅ {asset['id']} [{payload['operational_state']}] "
                                f"temp={payload['temperature']}°C "
                                f"health={payload['health_score']} "
                                f"record_id={data.get('record_id')}")
                else:
                    logger.warning(f"⚠️  {asset['id']} → HTTP {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"❌ Failed to send {asset['id']}: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    run()
