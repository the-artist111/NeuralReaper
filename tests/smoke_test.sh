#!/bin/bash
# Smoke test for NeuralReaper — verifies the MCP server initializes
# correctly inside the Docker image. This is the same handshake Claude
# Desktop performs on launch.
#
# Usage: bash tests/smoke_test.sh [image_name]

set -e

IMAGE="${1:-neuralreaper:latest}"

echo "[*] Running smoke test against image: $IMAGE"

RESPONSE=$(printf '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke-test","version":"1.0"}}}\n' | \
  docker run --rm -i \
    --network host \
    --cap-add NET_RAW \
    --cap-add NET_ADMIN \
    "$IMAGE" 2>/dev/null)

if echo "$RESPONSE" | grep -q "NeuralReaper"; then
    echo "[PASS] Server initialized successfully"
    echo "$RESPONSE"
    exit 0
else
    echo "[FAIL] Server did not respond as expected"
    echo "--- Raw output ---"
    echo "$RESPONSE"
    echo "-------------------"
    echo "[!] Common causes:"
    echo "    - Docker daemon not running"
    echo "    - Image not built yet (run: docker build -t neuralreaper:latest .)"
    echo "    - Container crashed on startup (check: docker logs)"
    exit 1
fi
