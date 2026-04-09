# ⚡ QSIM — Quantum-Safe Industrial Mesh

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ARM64-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Gateway-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Observability-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI/CD-D24939?style=for-the-badge&logo=jenkins&logoColor=white)

**A production-inspired Industry 4.0 Digital Twin Platform on Apple Silicon**

*B.Tech AI & Data Science — Semester VI DevOps Capstone Project*

[Live Dashboard](#live-endpoints) · [Architecture](#architecture) · [Quick Start](#quick-start) · [Chaos Engineering](#chaos-engineering-results)

</div>

---

## 🏭 What is QSIM?

QSIM (Quantum-Safe Industrial Mesh) is a **smart factory digital twin platform** that simulates 5 industrial assets — CNC Machine, Conveyor, Robot Arm, Sensor, and Press — sending real-time telemetry through a fully containerized, self-healing, observable Kubernetes platform.

Every 2 seconds, the factory simulator generates realistic sensor data (temperature, vibration, health scores, operational state) and sends it to a high-availability FastAPI gateway. The data is persisted to a Kubernetes PVC, visualized on a live Streamlit dashboard, monitored via Prometheus and Grafana, and deployed through a Jenkins health-gate CI/CD pipeline.

> **This is not a classroom exercise.** It is a miniature production-grade cloud-native platform demonstrating resilience engineering, observability, Infrastructure as Code, and Agile DevOps practices.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    macOS Apple Silicon M4 Pro                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Docker Desktop (ARM64/VirtioFS)          │  │
│  │                                                      │  │
│  │  ┌─────────────────────┐  ┌──────────────────────┐  │  │
│  │  │   qsim namespace    │  │  monitoring namespace │  │  │
│  │  │                     │  │                      │  │  │
│  │  │  [Generator]        │  │  [Prometheus]        │  │  │
│  │  │      ↓ HTTP POST    │  │  [Grafana]           │  │  │
│  │  │  [Gateway x2-6]     │  │  [AlertManager]      │  │  │
│  │  │      ↓ PVC          │  │  [kube-state-metrics]│  │  │
│  │  │  [Dashboard]        │  │  [node-exporter]     │  │  │
│  │  │  [HPA] [Ingress]    │  │                      │  │  │
│  │  └─────────────────────┘  └──────────────────────┘  │  │
│  │                                                      │  │
│  │  [Jenkins CI/CD]  ←→  [kubectl]  ←→  [Minikube]    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Traffic Flow
```
Browser → /etc/hosts → qsim-ui.local
       → minikube tunnel → NGINX Ingress
       → ClusterIP Service
       → Pod (load balanced across replicas)
```

---

## 🛠 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| **Language** | Python 3.11 | All backend and dashboard code |
| **API Framework** | FastAPI + Uvicorn | High-performance telemetry gateway |
| **Validation** | Pydantic | Strict payload schema enforcement |
| **Dashboard** | Streamlit + Plotly + Pandas | Live visual digital twin UI |
| **Metrics** | Prometheus Client | App-level metrics instrumentation |
| **Containers** | Docker Desktop ARM64 | Native Apple Silicon containerization |
| **Registry** | Docker Hub (10mozart/) | ARM64 image storage and distribution |
| **Orchestration** | Kubernetes + Minikube | Container scheduling and management |
| **Ingress** | NGINX Ingress Controller | Hostname-based traffic routing |
| **Autoscaling** | HPA | CPU-triggered elastic scaling (2-6 replicas) |
| **Storage** | PVC (1Gi) | Persistent telemetry log across pod restarts |
| **Config** | ConfigMap | Environment-based configuration management |
| **Monitoring** | Prometheus + Grafana | Full observability stack (14-panel dashboard) |
| **State Metrics** | kube-state-metrics | Pod health, replica counts, HPA state |
| **Node Metrics** | Node Exporter | VM-level CPU, memory, disk, network |
| **CI/CD** | Jenkins LTS | 5-stage health-gate deployment pipeline |
| **IaC** | Declarative YAML | All infrastructure defined as code |
| **Version Control** | Git + GitHub | Source control and project hosting |
| **Package Mgmt** | Helm | Kubernetes observability stack deployment |
| **Shell** | zsh | All automation scripts |

---

## 📁 Project Structure

```
qsim/
├── gateway/
│   ├── main.py              # FastAPI app — ingest, health, metrics, digital twin endpoints
│   ├── requirements.txt     # fastapi, uvicorn, pydantic, prometheus-client, httpx
│   └── Dockerfile           # ARM64-native Python 3.11 slim image
│
├── generator/
│   ├── factory_gen.py       # Simulates 5 factory assets, sends telemetry every 2s
│   ├── requirements.txt     # httpx
│   └── Dockerfile           # ARM64-native Python 3.11 slim image
│
├── dashboard/
│   ├── app.py               # Streamlit live dashboard — cards, charts, feed table
│   ├── requirements.txt     # streamlit, plotly, pandas, requests
│   └── Dockerfile           # ARM64-native Python 3.11 slim image
│
├── k8s/
│   └── manifests.yaml       # All K8s resources: namespace, configmap, pvc,
│                            # deployments, services, ingress, hpa
│
├── chaos.sh                 # 3 chaos experiments with MTTR measurement
├── start-qsim.sh            # One-command platform startup script
├── runbook.sh               # Step-by-step deployment guide
└── README.md                # This file
```

---

## 🚀 Quick Start

```zsh
./start-qsim.sh
```

This single command starts Minikube, tunnel, all pods, Grafana, Prometheus, and opens everything in your browser automatically. Platform is live in ~2 minutes.

---

## 🌐 Live Endpoints

| URL | Description |
|---|---|
| `http://qsim-ui.local` | Streamlit live dashboard — 5 machine cards, charts, telemetry feed |
| `http://qsim.local/health` | Gateway health check — uptime, record count, asset count |
| `http://qsim.local/assets` | Live digital twin state of all 5 assets |
| `http://qsim.local/telemetry` | Recent telemetry records from persistent storage |
| `http://qsim.local/metrics` | Prometheus scrape endpoint |
| `http://qsim.local/docs` | Auto-generated FastAPI Swagger documentation |
| `http://localhost:3000` | Grafana — 14-panel QSIM observability dashboard |
| `http://localhost:9090` | Prometheus — raw metrics and query interface |
| `http://localhost:8080` | Jenkins — CI/CD pipeline with build history |

---

## 🔬 Kubernetes Resources

| Resource | Name | Purpose |
|---|---|---|
| Namespace | `qsim` | Logical isolation for all platform components |
| Deployment | `qsim-gateway` | FastAPI gateway, 2-6 replicas, rolling update |
| Deployment | `qsim-generator` | Factory telemetry simulator, 1 replica |
| Deployment | `qsim-dashboard` | Streamlit UI, 1 replica |
| Service | `qsim-gateway-svc` | ClusterIP load balancer for gateway pods |
| Service | `qsim-dashboard-svc` | ClusterIP for dashboard pod |
| Ingress | `qsim-ingress` | Routes qsim.local → gateway |
| Ingress | `qsim-dashboard-ingress` | Routes qsim-ui.local → dashboard |
| HPA | `qsim-gateway-hpa` | Autoscales gateway 2→6 at 60% CPU |
| PVC | `qsim-data-pvc` | 1Gi persistent storage for telemetry logs |
| ConfigMap | `qsim-config` | Gateway URL, send interval, asset count |

---

## 🔥 Chaos Engineering Results

Three controlled experiments demonstrating autonomous self-healing:

| Experiment | Method | Result | MTTR |
|---|---|---|---|
| **Pod Kill** | `kubectl delete pod` (single) | New pod scheduled, probe passed | **10 seconds** |
| **Cascade Failure** | Force delete all gateway pods | Full platform recovery | **13 seconds** |
| **CPU Stress** | `stress-ng` workload injection | HPA triggered scale-out | Auto-scaled |

> **Key finding:** The platform's MTTR of 13 seconds under complete failure demonstrates that Kubernetes ReplicaSet controllers, combined with health probes and rolling restart policies, provide autonomous recovery without any human intervention.

---

## 📊 Observability Stack

The Grafana dashboard (`QSIM — Industrial Mesh Platform`) contains 14 panels:

- **6 Stat Cards** — Pods Ready, Total Restarts, CPU (millicores), Memory, Replicas, HPA count
- **CPU Usage by Pod** — Time series, per-pod breakdown
- **Memory Usage by Pod** — Time series with byte units
- **Memory Share** — Pie chart across all pods
- **CPU Share** — Donut chart across all pods
- **Pod Restart History** — Time series with threshold coloring
- **Pod Resource Quotas** — Table with requests and limits
- **Network I/O** — Receive and transmit by pod
- **HPA Scaling History** — Current vs Desired vs Max vs Min replicas

---

## 🔄 Jenkins CI/CD Pipeline

5-stage health-gate pipeline that enforces deployment quality:

```
Validate Manifests → Deploy → Rollout Gate → Health Gate → Smoke Test
                                   ↓                           ↓
                             [Failure] ←──────── Auto Rollback (kubectl rollout undo)
```

| Stage | What it does |
|---|---|
| **Validate** | `kubectl apply --dry-run` — catches YAML errors before touching cluster |
| **Deploy** | `kubectl apply` — declarative manifest application |
| **Rollout Gate** | Blocks until deployment reaches desired state or times out |
| **Health Gate** | Verifies pod readiness and service endpoint registration |
| **Smoke Test** | HTTP check against live ingress endpoint |

---

## 📈 Platform Metrics

| Metric | Value |
|---|---|
| Total records ingested | 70,000+ |
| Assets tracked | 5 |
| MTTR (cascade failure) | 13 seconds |
| Gateway replicas | 2–6 (HPA) |
| Persistent storage | 1Gi PVC |
| Telemetry interval | 2 seconds |
| Prometheus scrape interval | 15 seconds |
| Dashboard refresh interval | 3 seconds |

---

## 🐳 Docker Images

```
10mozart/qsim-gateway:v1     — FastAPI telemetry gateway
10mozart/qsim-generator:v1   — Factory asset simulator
10mozart/qsim-dashboard:v4   — Streamlit live dashboard
```

All images are built for `linux/arm64` (Apple Silicon native).

---

## ⚠️ Platform Constraints

This platform runs on macOS with Docker Desktop and Minikube. Two honest architectural constraints:

1. **Single-node cluster** — Minikube uses one node, so pod anti-affinity across nodes cannot be demonstrated. In production EKS/GKE, replicas would spread across physical nodes.

2. **Darwin observability gap** — Node Exporter runs inside the Minikube Linux VM, not on the physical Mac. Darwin host metrics (memory pressure, thermal state) are not observable via Prometheus. Container-level metrics via cAdvisor are fully accurate.

---

## 👨‍💻 Author

**Joshua Rebello**
B.Tech Artificial Intelligence & Data Science
NMIMS Indore (MPSTME) — Semester VI
