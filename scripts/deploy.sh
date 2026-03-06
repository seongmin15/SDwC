
#!/bin/bash
set -e

CLUSTER_NAME="sdwc"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Creating k3d cluster..."
k3d cluster create $CLUSTER_NAME -p "8080:80@loadbalancer" || echo "Cluster already exists"

echo "🐳 Building Docker images..."
docker build -f sdwc-api/Dockerfile -t sdwc-api:local .
docker build -f sdwc-web/Dockerfile -t sdwc-web:local .

echo "📦 Importing images into k3d..."
k3d image import sdwc-api:local sdwc-web:local -c $CLUSTER_NAME

echo "☸️ Applying manifests..."
kubectl apply -f infra/sdwc-api/deployment.yaml
kubectl apply -f infra/sdwc-web/deployment.yaml
kubectl apply -f infra/ingress.yaml

echo "⏳ Waiting for pods..."
kubectl wait --for=condition=Ready pod --all --timeout=120s

echo "🌐 Testing..."
curl http://localhost:8080/health || true

echo "✅ Deployment complete"
