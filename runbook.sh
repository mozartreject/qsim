#!/usr/bin/env zsh
# =============================================================================
# QSIM — Complete Build, Push, Deploy Runbook
# Run each section in order. Do NOT skip steps.
# =============================================================================

# =============================================================================
# STEP 1: Build Gateway Image (ARM64)
# =============================================================================
cd ~/Desktop/qsim/gateway

docker build \
  --platform linux/arm64 \
  -t 10mozart/qsim-gateway:v1 \
  .

# Verify image was built
docker images | grep qsim-gateway

# =============================================================================
# STEP 2: Build Generator Image (ARM64)
# =============================================================================
cd ~/Desktop/qsim/generator

docker build \
  --platform linux/arm64 \
  -t 10mozart/qsim-generator:v1 \
  .

docker images | grep qsim-generator

# =============================================================================
# STEP 3: Push Both Images to Docker Hub
# (Must be logged in: docker login)
# =============================================================================
docker push 10mozart/qsim-gateway:v1
docker push 10mozart/qsim-generator:v1

# =============================================================================
# STEP 4: Load Images into Minikube
# (Faster than pulling from Docker Hub every time)
# =============================================================================
minikube image load 10mozart/qsim-gateway:v1
minikube image load 10mozart/qsim-generator:v1

# Verify images are in Minikube
minikube image ls | grep qsim

# =============================================================================
# STEP 5: Apply Kubernetes Manifests
# =============================================================================
cd ~/Desktop/qsim/k8s

kubectl apply -f manifests.yaml

# =============================================================================
# STEP 6: Wait for Gateway to be Ready
# =============================================================================
kubectl rollout status deployment/qsim-gateway -n qsim --timeout=120s

kubectl get pods -n qsim

# =============================================================================
# STEP 7: Update /etc/hosts for local DNS
# =============================================================================
# Get minikube IP first:
# minikube ip
# Then add to /etc/hosts:
# 127.0.0.1  qsim.local
# (Use 127.0.0.1 because minikube tunnel routes through localhost on macOS)

# =============================================================================
# STEP 8: Start Minikube Tunnel (in a separate terminal tab)
# =============================================================================
# Run this in a NEW terminal tab and leave it running:
# minikube tunnel

# =============================================================================
# STEP 9: Test the Gateway
# =============================================================================
# Health check
curl http://qsim.local/health

# Send a test telemetry payload manually
curl -X POST http://qsim.local/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": "TEST-001",
    "asset_type": "CNC_MACHINE",
    "temperature": 72.5,
    "vibration": 12.3,
    "health_score": 0.92,
    "operational_state": "RUNNING"
  }'

# View ingested records
curl http://qsim.local/telemetry

# View active assets
curl http://qsim.local/assets

# View Prometheus metrics
curl http://qsim.local/metrics

# =============================================================================
# STEP 10: Watch Generator Logs (live telemetry flowing)
# =============================================================================
kubectl logs -n qsim -l app=qsim-generator -f
