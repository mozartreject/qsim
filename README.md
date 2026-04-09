# ⚡ QSIM — Quantum-Safe Industrial Mesh

A production-inspired Industry 4.0 Digital Twin Platform built on Kubernetes.

## What is QSIM?

QSIM simulates a smart factory with 5 industrial assets (CNC Machine, Conveyor, Robot Arm, Sensor, Press) sending real-time telemetry — temperature, vibration, health scores, and operational state — through a distributed, self-healing, observable backend platform.

## Architecture

Factory Generator (Python) → FastAPI Gateway (3 replicas) → Streamlit Dashboard → Prometheus + Grafana → Jenkins CI/CD

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| API | FastAPI + Pydantic + Uvicorn |
| Dashboard | Streamlit + Plotly + Pandas |
| Containers | Docker ARM64 |
| Orchestration | Kubernetes Minikube |
| Observability | Prometheus + Grafana |
| CI/CD | Jenkins LTS |

## Project Structure

gateway/ — FastAPI telemetry ingestion API
generator/ — Factory asset telemetry simulator
dashboard/ — Streamlit live visual dashboard
k8s/ — Kubernetes manifests
chaos.sh — Chaos engineering experiments
start-qsim.sh — One-command platform startup

## Quick Start

./start-qsim.sh

## Live Endpoints

qsim-ui.local — Streamlit dashboard
qsim.local/health — Gateway health
qsim.local/assets — Live asset states
localhost:3000 — Grafana
localhost:9090 — Prometheus
localhost:8080 — Jenkins

## Chaos Engineering Results

Pod Kill — Recovery in 10 seconds
Cascade Kill — MTTR 13 seconds
CPU Stress — HPA scaled automatically

## Key Metrics

70000+ telemetry records persisted
5 factory assets as digital twins
13 seconds MTTR
2-6 replicas auto-scaled by HPA
1Gi persistent storage via PVC

## Docker Images

10mozart/qsim-gateway:v1
10mozart/qsim-generator:v1
10mozart/qsim-dashboard:v4

## Author

Joshua Rebello — B.Tech AI & Data Science, NMIMS Indore
