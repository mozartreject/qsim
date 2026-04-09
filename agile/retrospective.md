# 🔄 QSIM — Sprint Retrospectives

## What is a Retrospective?
At the end of each sprint, the team reflects on what went well, what didn't, and what to improve. This drives continuous improvement — a core Agile principle.

---

## Sprint 1 Retrospective — Core Platform

### ✅ What Went Well
- **Declarative YAML-first approach** paid off immediately. Every resource was reproducible and version-controlled from day one.
- **Docker multi-arch build** with `--platform linux/arm64` worked cleanly on Apple Silicon without any compatibility issues.
- **FastAPI + Pydantic** combination gave us free input validation and auto-generated API docs at `/docs` with zero extra effort.
- **Minikube addons** (ingress, metrics-server) installed cleanly and worked immediately.

### ❌ What Didn't Go Well
- **Port mismatch** — wrote probes for port 3000 but the app (nginx-based) actually runs on port 80. Caused pods to crash-loop for several minutes.
- **imagePullPolicy: Always** caused pods to hang when Docker Hub was slow. Should have used `IfNotPresent` for local development from the start.

### 🔧 Action Items for Next Sprint
- Always run `docker run` locally to inspect the image before writing Kubernetes manifests
- Set `imagePullPolicy: IfNotPresent` for local development
- Add `minikube image load` step to runbook

### 📊 Sprint Metrics
- User stories completed: 3/3
- Blockers encountered: 2
- Blockers resolved: 2
- Records ingested by end of sprint: ~8,000

---

## Sprint 2 Retrospective — Observability & CI/CD

### ✅ What Went Well
- **kube-prometheus-stack Helm chart** deployed the entire observability stack (Prometheus, Grafana, AlertManager, kube-state-metrics, Node Exporter) in a single command. Saves hours of manual YAML writing.
- **Jenkins PATH fix** — adding `/opt/homebrew/bin` to the pipeline environment variable resolved the kubectl not found issue cleanly.
- **Chaos experiments** produced clear, measurable MTTR data (13 seconds) that can be cited directly in academic work.
- **PromQL queries** in Grafana Explore confirmed data availability before building dashboard panels.

### ❌ What Didn't Go Well
- **Grafana login** — the adminPassword set via Helm didn't take effect because the initial install timed out. Resolved by extracting the actual password from the Kubernetes secret.
- **Grafana dashboard no-data** — panels showed no data because queries used `container!=""` filter which doesn't match Minikube's cAdvisor label format. Required inspecting raw Prometheus labels to identify the issue.
- **Jenkins health gate** — timed out waiting for 3 pods when HPA had scaled down to 2. Fixed by changing the wait logic to check for at least 1 ready pod instead of all desired replicas.

### 🔧 Action Items for Next Sprint
- Always verify exact Prometheus label names via `/api/v1/query` before writing PromQL
- Test Grafana login immediately after Helm install, not after 2 hours
- Document HPA behavior in pipeline health gate logic

### 📊 Sprint Metrics
- User stories completed: 3/3
- Blockers encountered: 3
- Blockers resolved: 3
- MTTR measured: 13 seconds
- Grafana panels working: 14/14

---

## Sprint 3 Retrospective — Dashboard & Polish

### ✅ What Went Well
- **Streamlit + Plotly** combination produced a genuinely impressive visual dashboard in pure Python. The asset cards with color-coded state borders and health progress bars look production-grade.
- **CSS injection via `st.markdown`** allowed full custom styling within Streamlit's constraints — dark theme, monospace fonts, glowing borders.
- **GitHub CLI (`gh`)** made repo creation and push a single command. No manual repo setup needed.
- **One-command startup script** (`start-qsim.sh`) using `osascript` to open new Terminal tabs works reliably on macOS.

### ❌ What Didn't Go Well
- **Dashboard image rebuild cycle** took multiple iterations (v1 → v4) due to environment variable not being read (missing `import os`), syntax error in f-string, and cached image in Minikube.
- **GATEWAY_URL hardcoded** in original app.py — should have used `os.environ.get()` from the start to avoid in-cluster DNS issues.
- **f-string nesting** — Python 3.11 doesn't allow `strftime()` calls with quotes inside f-strings. Required splitting into separate variable assignment.

### 🔧 Action Items (if continuing development)
- Always use `os.environ.get()` for any URL or config value in containerized apps
- Test f-strings with nested quotes in Python before containerizing
- Add `.dockerignore` to avoid copying unnecessary files into images

### 📊 Sprint Metrics
- User stories completed: 4/4
- Dashboard image versions: 4 (v1 → v4)
- Blockers encountered: 3
- Blockers resolved: 3
- Final telemetry record count: 70,000+

---

## Overall Project Retrospective

### 🏆 Top 3 Successes
1. **End-to-end platform in one day** — from zero to a fully observable, self-healing, CI/CD-managed Kubernetes platform with a live visual dashboard.
2. **Measured resilience** — MTTR of 13 seconds is a concrete, empirically measured engineering outcome that demonstrates platform maturity.
3. **Real data** — 70,000+ actual telemetry records persisted to a PVC. This is not a simulated demo — it is real data flowing through a real distributed system.

### 📚 Top 3 Learnings
1. **Declarative over imperative** — writing YAML manifests first and applying them consistently is far more reliable than running imperative `kubectl` commands. Everything is reproducible.
2. **Observe before you build dashboards** — checking raw Prometheus labels via the API before writing PromQL saved significant debugging time in Sprint 3.
3. **Platform constraints are not weaknesses** — honestly documenting the Darwin/Linux observability gap and single-node Minikube limitation demonstrates architectural awareness, not ignorance.

### 🔮 If Given More Time
- Add ML-based anomaly detection on health score trends
- Implement multi-node Minikube to demonstrate true pod anti-affinity
- Add TLS termination at the Ingress layer
- Implement GitHub Actions for automated image builds on push
- Add Alertmanager rules to fire on FAULT state frequency
