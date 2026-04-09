#!/usr/bin/env zsh
# =============================================================================
# QSIM Chaos Engineering Suite
# =============================================================================

NS="qsim"

echo "=== CHAOS EXPERIMENT 1: Kill a Gateway Pod ==="
echo "Expected: Kubernetes replaces it within ~20s. 2 remaining pods keep serving."
POD=$(kubectl get pods -n $NS -l app=qsim-gateway -o jsonpath='{.items[0].metadata.name}')
echo "Killing: $POD"
kubectl delete pod $POD -n $NS
echo "Watching recovery..."
kubectl get pods -n $NS -w &
sleep 30
kill %1 2>/dev/null
echo "Restart count after recovery:"
kubectl get pods -n $NS -l app=qsim-gateway

echo ""
echo "=== CHAOS EXPERIMENT 2: Kill ALL Gateway Pods (MTTR test) ==="
echo "Expected: Full recovery in 30-60s. Measures worst-case MTTR."
START=$(date +%s)
kubectl delete pods -n $NS -l app=qsim-gateway --grace-period=0 --force
until kubectl get pods -n $NS -l app=qsim-gateway | grep -q "2/2\|3/3\|1/1"; do
  sleep 2
done
END=$(date +%s)
echo "MTTR: $((END - START)) seconds"

echo ""
echo "=== CHAOS EXPERIMENT 3: CPU Stress (trigger HPA) ==="
kubectl run cpu-stressor --image=alexeiled/stress-ng:latest-ubuntu \
  --namespace=$NS \
  --restart=Never \
  -- --cpu 2 --timeout 60s
echo "Watch HPA scale up:"
kubectl get hpa -n $NS -w &
sleep 75
kill %1 2>/dev/null
kubectl delete pod cpu-stressor -n $NS --ignore-not-found

echo ""
echo "=== VERIFY: Platform fully recovered ==="
kubectl get pods -n $NS
kubectl get hpa -n $NS
