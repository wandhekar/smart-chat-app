#!/bin/bash

# If using private GHCR repo, create secret first
# kubectl create secret docker-registry ghcr-secret \
#   --docker-server=ghcr.io \
#   --docker-username=YOUR_GITHUB_USERNAME \
#   --docker-password=YOUR_GITHUB_TOKEN \
#   --docker-email=YOUR_EMAIL

echo "Setting up minikube docker environment..."
eval $(minikube docker-env)

echo "Building local images (backend & frontend)..."
docker build -t my-backend:latest ./backend
docker build -t my-frontend:latest ./frontend

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/ollama-pvc.yaml
kubectl apply -f k8s/ollama-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=ollama --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s

echo "Checking ollama models..."
kubectl exec -it deployment/ollama -- ollama list

echo "Getting access info..."
echo "Minikube IP: $(minikube ip)"
echo "Add to /etc/hosts: echo '$(minikube ip) my-app.local' | sudo tee -a /etc/hosts"
echo "Then access: http://my-app.local"
echo ""
echo "Or use port-forward:"
echo "kubectl port-forward service/frontend-service 8501:8501"