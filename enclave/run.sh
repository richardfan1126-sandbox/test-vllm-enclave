#!/bin/bash

set -e

# Assign local loopback address
ifconfig lo 127.0.0.1

# Start traffic forwarder
/usr/bin/socat -t 30 VSOCK-LISTEN:1000,fork,reuseaddr TCP:127.0.0.1:8000 &

# Start vLLM server
vllm serve "/app/local_model" \
    --port 8080 \
    --dtype auto \
    --api-key token-abc123 &

# Start app
/opt/venv/bin/python /app/src/main.py &

# Exit if any process exit
wait -n
exit $?
