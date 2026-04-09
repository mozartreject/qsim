#!/usr/bin/env zsh
echo "🚀 Starting QSIM Platform..."
minikube start
osascript -e 'tell application "Terminal" to do script "minikube tunnel"'
kubectl wait --for=condition=Ready node/minikube --timeout=60s
echo "⏳ Waiting for pods..."
kubectl wait --for=condition=Ready pod -l app=qsim-gateway -n qsim --timeout=120s
kubectl wait --for=condition=Ready pod -l app=qsim-generator -n qsim --timeout=60s
kubectl wait --for=condition=Ready pod -l app=qsim-dashboard -n qsim --timeout=120s
osascript -e 'tell application "Terminal" to do script "kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring"'
osascript -e 'tell application "Terminal" to do script "kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring"'
sleep 5
open http://qsim-ui.local
open http://localhost:3000
open http://localhost:9090
open http://localhost:8080
echo "✅ QSIM is live!"
kubectl get pods -n qsim
