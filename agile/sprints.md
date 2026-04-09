# 🏃 QSIM — Agile Sprint Log

## Project: QSIM — Quantum-Safe Industrial Mesh
## Methodology: Agile Scrum (3 Sprints)
## Team: Joshua Rebello
## Duration: 1 Development Cycle

---

## Sprint 0 — Foundation & Planning
**Duration:** Day 1, Morning
**Goal:** Define system architecture, set up development environment, establish infrastructure baseline.

### Tasks Completed
- Defined system vision: Smart Factory Digital Twin on Kubernetes
- Identified 5 factory asset types: CNC Machine, Conveyor, Robot Arm, Sensor, Press
- Set up Minikube cluster on Apple Silicon (ARM64)
- Enabled NGINX Ingress and metrics-server addons
- Configured Docker Desktop with VirtioFS driver
- Installed Helm, kubectl, Jenkins LTS via Homebrew
- Defined Kubernetes namespace strategy (qsim / monitoring)
- Created project folder structure

### Outcome
✅ Local Kubernetes cluster operational
✅ Development environment fully configured
✅ Architecture design finalized

### Retrospective
**What went well:** Environment setup was smooth with Homebrew
**Blocker:** ARM64 image compatibility needed explicit `--platform linux/arm64` flag

---

## Sprint 1 — Core Platform Build
**Duration:** Day 1, Afternoon
**Goal:** Build and deploy the telemetry pipeline — generator, gateway, and Kubernetes orchestration.

### User Stories Delivered
- As a factory operator, I want telemetry from all 5 machines ingested automatically
- As a platform engineer, I want the gateway to self-heal if it crashes
- As a data engineer, I want telemetry persisted across pod restarts

### Tasks Completed
- Built FastAPI gateway with `/ingest`, `/health`, `/ready`, `/assets`, `/telemetry`, `/metrics` endpoints
- Implemented Pydantic payload validation (temperature range, health score bounds, state enum)
- Implemented Prometheus metrics instrumentation (per-asset gauges, latency histogram, counter)
- Built factory generator simulating 5 assets with realistic state distribution
- Created ARM64-native Dockerfiles for both services
- Built and pushed images to Docker Hub (10mozart/)
- Loaded images into Minikube
- Wrote all Kubernetes manifests: namespace, configmap, PVC, deployments, services, ingress, HPA
- Deployed full stack to Minikube
- Configured /etc/hosts for local DNS (qsim.local)
- Verified 3 replicas running, readiness probes passing
- Confirmed telemetry flowing at 2s intervals

### Outcome
✅ Gateway ingesting telemetry from all 5 assets
✅ 8,000+ records persisted within first hour
✅ Self-healing verified — pod kill recovery in 10 seconds
✅ PVC confirmed bound and data surviving restarts

### Retrospective
**What went well:** Declarative YAML-first approach made deployments reproducible
**Blocker:** Port 3000 mismatch — app runs on port 80 (nginx), not 3000. Fixed by inspecting Docker image.
**Learning:** Always `docker run` the image locally before writing Kubernetes probes

---

## Sprint 2 — Observability & CI/CD
**Duration:** Day 1, Evening
**Goal:** Wire up full observability stack and implement CI/CD pipeline with health gates.

### User Stories Delivered
- As an SRE, I want to see CPU and memory for every pod in real time
- As a DevOps engineer, I want deployments to fail automatically if pods are unhealthy
- As an operator, I want a dashboard showing platform health at a glance

### Tasks Completed
- Deployed kube-prometheus-stack via Helm (Prometheus, Grafana, AlertManager, kube-state-metrics, Node Exporter)
- Resolved ARM64 image compatibility for all monitoring components
- Configured ServiceMonitor for QSIM gateway scraping
- Built custom Grafana dashboard (14 panels): stat cards, time series, pie charts, donut, table, network I/O, HPA scaling
- Debugged Prometheus label mismatch (container filter causing no-data)
- Configured Jenkins LTS CI/CD pipeline (5 stages: validate, deploy, rollout gate, health gate, smoke test)
- Fixed Jenkins PATH issue for kubectl on macOS
- Implemented automatic rollback on pipeline failure
- Ran 3 chaos engineering experiments, measured MTTR
- Documented chaos results: pod kill 10s, cascade 13s, CPU stress HPA trigger

### Outcome
✅ Grafana dashboard fully populated with live data
✅ Jenkins pipeline passing all 5 stages
✅ Chaos experiments completed with MTTR = 13 seconds
✅ Prometheus scraping both infrastructure and application metrics

### Retrospective
**What went well:** kube-prometheus-stack Helm chart covers entire observability stack in one command
**Blocker:** Grafana login issue — resolved by extracting password from Kubernetes secret
**Blocker:** Dashboard panels showing no data — fixed by removing container label filter incompatible with Minikube cAdvisor
**Learning:** Always verify exact Prometheus label names before writing PromQL

---

## Sprint 3 — Dashboard & Polish
**Duration:** Day 2, Morning
**Goal:** Build live visual dashboard, push to GitHub, finalize documentation.

### User Stories Delivered
- As a factory manager, I want a visual control room showing all 5 machines in real time
- As a professor, I want to see the project on GitHub with clear documentation
- As a student, I want one command to start the entire platform

### Tasks Completed
- Built Streamlit dashboard with 5 asset cards (color-coded by state), 4 Plotly charts, live telemetry feed table
- Fixed gateway URL for in-cluster communication (qsim-gateway-svc internal DNS)
- Rebuilt dashboard image v2, v3, v4 iteratively
- Configured qsim-ui.local ingress routing
- Wrote start-qsim.sh one-command startup script
- Initialized Git repository
- Created GitHub repo (mozartreject/qsim)
- Pushed all code, manifests, scripts
- Wrote comprehensive README with architecture diagram, stack table, chaos results, endpoint reference
- Added anomaly detection module
- Created Agile documentation folder

### Outcome
✅ Live Streamlit dashboard at qsim-ui.local
✅ GitHub repo published at github.com/mozartreject/qsim
✅ One-command startup working
✅ 70,000+ telemetry records persisted across entire development cycle

### Retrospective
**What went well:** Streamlit + Plotly combination gives production-quality visuals in pure Python
**Blocker:** imagePullPolicy: Always caused dashboard pod to hang pulling from Docker Hub instead of local cache
**Learning:** Use IfNotPresent for local development, Always only for production with reliable registry access

---

## Overall Project Metrics

| Metric | Value |
|---|---|
| Total sprints | 3 + planning sprint |
| User stories delivered | 9 |
| Services built | 3 (gateway, generator, dashboard) |
| Docker images published | 3 |
| Kubernetes resources deployed | 11 |
| Lines of code | ~1,200 |
| Telemetry records generated | 70,000+ |
| MTTR achieved | 13 seconds |
| CI/CD pipeline stages | 5 |
| Grafana panels | 14 |
