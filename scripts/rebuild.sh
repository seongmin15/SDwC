
#!/bin/bash
set -e

CLUSTER_NAME="sdwc"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🐳 Rebuilding images..."
docker build -f sdwc-api/Dockerfile -t sdwc-api:local .
docker build -f sdwc-web/Dockerfile -t sdwc-web:local .

echo "📦 Importing images..."
k3d image import sdwc-api:local sdwc-web:local -c $CLUSTER_NAME

echo "🔄 Restarting deployments..."
kubectl rollout restart deployment sdwc-api
kubectl rollout restart deployment sdwc-web

echo "⏳ Waiting..."
kubectl rollout status deployment sdwc-api
kubectl rollout status deployment sdwc-web

echo "✅ Rebuild complete"
