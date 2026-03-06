
#!/bin/bash

CLUSTER_NAME="sdwc"

echo "🧹 Deleting k3d cluster..."
k3d cluster delete $CLUSTER_NAME

echo "✅ Cluster removed"
