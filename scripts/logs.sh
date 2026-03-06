
#!/bin/bash

echo "📜 SDWC API Logs"
kubectl logs -l app=sdwc-api -f

echo "📜 SDWC WEB Logs"
kubectl logs -l app=sdwc-web -f
