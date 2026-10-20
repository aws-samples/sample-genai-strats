#!/usr/bin/env bash
# Polls an AgentCore memory until its status is ACTIVE.
# Usage: wait-memory-active.sh <memory-id> <region>
set -euo pipefail

MEMORY_ID="$1"
REGION="$2"
MAX_ATTEMPTS=120
SLEEP_SECONDS=5

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  STATUS=$(aws bedrock-agentcore-control get-memory \
    --memory-id "$MEMORY_ID" \
    --region "$REGION" \
    --query 'memory.status' \
    --output text)
  echo "memory $MEMORY_ID status: $STATUS (attempt $i/$MAX_ATTEMPTS)"
  if [ "$STATUS" = "ACTIVE" ]; then
    exit 0
  fi
  sleep "$SLEEP_SECONDS"
done

echo "timed out waiting for memory $MEMORY_ID to become ACTIVE"
exit 1
