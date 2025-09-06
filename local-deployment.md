Deployment Instructions
Prerequisites

Install Minikube: curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube
Start Minikube: minikube start --memory=8192 --cpus=4
Enable ingress: minikube addons enable ingress

Local Deployment Steps

Clone and prepare:
git clone your-repo
cd smart-chat-app

Build images locally for Minikube:
eval $(minikube docker-env)
docker build -t smart-chat-frontend:latest ./frontend
docker build -t smart-chat-backend:latest ./backend

Update Kubernetes manifests for local development:
# Replace registry URLs with local tags
sed -i 's|your-registry/smart-chat-frontend:latest|smart-chat-frontend:latest|g' k8s/frontend-deployment.yaml
sed -i 's|your-registry/smart-chat-backend:latest|smart-chat-backend:latest|g' k8s/backend-deployment.yaml

Deploy to Minikube:
kubectl apply -f k8s/

Pull Ollama model (after deployment):
kubectl exec -it deployment/ollama -- ollama pull llama2

Access the application:
minikube service frontend-service --url

Production Considerations

Security: Implement proper authentication, HTTPS, network policies
Monitoring: Add Prometheus, Grafana for monitoring
Logging: Implement centralized logging with ELK stack
Scaling: Configure HPA (Horizontal Pod Autoscaler)
Storage: Use persistent volumes for Ollama data
Secrets: Use Kubernetes secrets for sensitive data
Resource Management: Fine-tune resource requests and limits
