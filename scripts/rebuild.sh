
#!/bin/bash
set -e

CLUSTER_NAME="sdwc"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

API_IMAGE="ghcr.io/seongmin15/sdwc/sdwc-api:latest"
WEB_IMAGE="ghcr.io/seongmin15/sdwc/sdwc-web:latest"

echo "🐳 Rebuilding images..."
docker build -f sdwc-api/Dockerfile -t $API_IMAGE .
docker build -f sdwc-web/Dockerfile -t $WEB_IMAGE .

echo "📦 Importing images..."
k3d image import $API_IMAGE $WEB_IMAGE -c $CLUSTER_NAME

echo "🔄 Restarting deployments..."
kubectl rollout restart deployment sdwc-api
kubectl rollout restart deployment sdwc-web

echo "⏳ Waiting..."
kubectl rollout status deployment sdwc-api
kubectl rollout status deployment sdwc-web

echo "✅ Rebuild complete"
