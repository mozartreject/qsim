# 📋 QSIM — User Stories

## Project: QSIM — Quantum-Safe Industrial Mesh
## Format: As a [role], I want [feature], so that [benefit]

---

## Epic 1: Telemetry Ingestion

### US-001 — Factory Telemetry Simulation
**As a** factory simulation engineer,
**I want** a Python-based simulator that generates realistic telemetry for 5 factory assets every 2 seconds,
**So that** I can test the platform with continuous, realistic data without needing physical hardware.

**Acceptance Criteria:**
- [ ] Simulator generates temperature, vibration, health score, and operational state per asset
- [ ] State distribution is realistic (70% RUNNING, 20% IDLE, 5% FAULT, 5% MAINTENANCE)
- [ ] Simulator runs continuously until stopped
- [ ] Each asset has a unique ID and type

**Status:** ✅ Done | **Sprint:** 1

---

### US-002 — Telemetry Ingestion API
**As a** platform engineer,
**I want** a REST API that receives and validates telemetry payloads,
**So that** invalid data is rejected before it reaches storage.

**Acceptance Criteria:**
- [ ] POST /ingest endpoint accepts telemetry JSON
- [ ] Pydantic validates all fields with strict type and range checks
- [ ] Invalid payloads return HTTP 422 with clear error message
- [ ] Valid payloads return HTTP 200 with record ID

**Status:** ✅ Done | **Sprint:** 1

---

### US-003 — Persistent Telemetry Storage
**As a** data engineer,
**I want** all ingested telemetry to survive pod restarts,
**So that** historical data is not lost during deployments or failures.

**Acceptance Criteria:**
- [ ] Gateway writes every record to /data/telemetry.jsonl
- [ ] /data is mounted from a Kubernetes PVC
- [ ] After pod restart, all previous records are still accessible
- [ ] GET /telemetry returns records from persistent storage

**Status:** ✅ Done | **Sprint:** 1

---

## Epic 2: High Availability & Resilience

### US-004 — Self-Healing Gateway
**As an** SRE,
**I want** the gateway to automatically recover from crashes without manual intervention,
**So that** the platform maintains availability even under failure conditions.

**Acceptance Criteria:**
- [ ] Gateway runs with minimum 2 replicas
- [ ] Liveness probe detects deadlocked pods and restarts them
- [ ] Readiness probe removes unhealthy pods from load balancer
- [ ] Startup probe prevents premature liveness checks
- [ ] Pod kill recovery time < 30 seconds

**Status:** ✅ Done | **Sprint:** 1 | **MTTR:** 10 seconds

---

### US-005 — Elastic Autoscaling
**As a** platform engineer,
**I want** the gateway to automatically scale up under high CPU load,
**So that** the platform handles traffic spikes without manual intervention.

**Acceptance Criteria:**
- [ ] HPA configured with min=2, max=6 replicas
- [ ] Scale-out triggers at 60% average CPU utilization
- [ ] Scale-down stabilization window prevents thrashing
- [ ] HPA scaling events visible in Grafana

**Status:** ✅ Done | **Sprint:** 2

---

## Epic 3: Observability

### US-006 — Infrastructure Monitoring
**As an** SRE,
**I want** real-time CPU, memory, and network metrics for every pod,
**So that** I can identify resource bottlenecks before they cause failures.

**Acceptance Criteria:**
- [ ] Prometheus scrapes all pods every 15 seconds
- [ ] Grafana shows CPU and memory time series per pod
- [ ] Pie charts show resource distribution across pods
- [ ] Pod restart count is visible and alerts on spikes

**Status:** ✅ Done | **Sprint:** 2

---

### US-007 — Application Metrics
**As a** data engineer,
**I want** per-asset telemetry metrics exposed to Prometheus,
**So that** I can track asset health trends over time in Grafana.

**Acceptance Criteria:**
- [ ] /metrics endpoint exposes Prometheus-compatible metrics
- [ ] qsim_asset_temperature_celsius gauge per asset
- [ ] qsim_asset_health_score gauge per asset
- [ ] qsim_telemetry_received_total counter per asset

**Status:** ✅ Done | **Sprint:** 2

---

## Epic 4: Visualization

### US-008 — Live Factory Dashboard
**As a** factory manager,
**I want** a visual control room showing the real-time state of all 5 machines,
**So that** I can immediately identify which assets are in FAULT or MAINTENANCE state.

**Acceptance Criteria:**
- [ ] 5 asset cards color-coded by state (green/yellow/red/purple)
- [ ] Each card shows temperature, vibration, health score, and state
- [ ] Health bar shows visual progress toward critical threshold
- [ ] FAULT state cards pulse with red border animation
- [ ] Dashboard auto-refreshes every 3 seconds

**Status:** ✅ Done | **Sprint:** 3

---

### US-009 — Telemetry Analytics Charts
**As a** data analyst,
**I want** time-series charts showing temperature and health score trends per asset,
**So that** I can identify degrading assets before they reach critical failure.

**Acceptance Criteria:**
- [ ] Temperature over time chart with per-asset color coding
- [ ] Health score chart with critical threshold line at 0.6
- [ ] State distribution bar chart showing RUNNING/IDLE/FAULT/MAINTENANCE counts
- [ ] Vibration vs health scatter plot showing correlation

**Status:** ✅ Done | **Sprint:** 3

---

## Epic 5: CI/CD

### US-010 — Health-Gate Deployment Pipeline
**As a** DevOps engineer,
**I want** every deployment to pass automated health checks before being considered successful,
**So that** broken deployments are automatically detected and rolled back.

**Acceptance Criteria:**
- [ ] Pipeline validates YAML manifests before deploying
- [ ] Pipeline blocks until rollout completes
- [ ] Pipeline verifies pod readiness after deployment
- [ ] Pipeline runs HTTP smoke test against live endpoint
- [ ] Failed deployments trigger automatic rollback

**Status:** ✅ Done | **Sprint:** 2

---

## Story Points Summary

| Epic | Stories | Status |
|---|---|---|
| Telemetry Ingestion | US-001, US-002, US-003 | ✅ All Done |
| High Availability | US-004, US-005 | ✅ All Done |
| Observability | US-006, US-007 | ✅ All Done |
| Visualization | US-008, US-009 | ✅ All Done |
| CI/CD | US-010 | ✅ All Done |

**Total: 10 user stories — 10 delivered**
