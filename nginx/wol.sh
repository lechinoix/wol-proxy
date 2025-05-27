#!/bin/bash

echo "Content-Type: text/plain"

# Send WoL
wakeonlan 44:fa:66:72:e9:b7 > /dev/null
# Wait for the server to come online (max 30s)
timeout=30
elapsed=0

while true; do
  status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 1 http://192.168.100.2:2283/)

  if [[ $status_code -lt 500 && $status_code -ne 000 ]]; then
    break
  fi

  sleep 1
  elapsed=$((elapsed + 1))
  if [ $elapsed -ge $timeout ]; then
    echo "Status: 504 Gateway Timeout"
    echo ""
    echo "Server didn't respond with a valid <500 status after $timeout seconds."
    exit 0
  fi
done

# Redirect to the original URL (stored in ORIGINAL_URI passed by NGINX)
target="${ORIGINAL_URI:-/}"

echo "Status: 307 Temporary Redirect"
echo "Location: $target"
echo "Content-Type: text/plain"
echo ""
echo "Server is up. Redirecting to $target..."

