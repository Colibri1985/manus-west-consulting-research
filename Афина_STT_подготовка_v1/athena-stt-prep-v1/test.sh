#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
# Mandatory values from preflight: actual effective IDs, not executor UID.
: "${GATEWAY_UID:?Set actual effective gateway UID from preflight}"
: "${GATEWAY_GID:?Set actual effective gateway GID from preflight}"
[[ "$GATEWAY_UID" =~ ^[0-9]+$ && "$GATEWAY_GID" =~ ^[0-9]+$ ]] || exit 2
image='athena-hermes-stt:fw1.2.1-av16.1.0-v1'
cache='/srv/hermes-agent/athena-stt-cache'
# Do not add groups: model cache is owned by the exact UID/GID. A missing required
# supplementary-group dependency is a failed test, not grounds to widen rights.
if [ "${1:-}" = download ]; then
 [ "${ATHENA_APPROVE_DOWNLOAD:-}" = YES ] || { printf '%s\n' 'STOP: model download approval required'; exit 2; }
 [ -d "$cache" ] || { printf '%s\n' 'STOP: prepare dedicated cache with gateway owner first'; exit 2; }
 sudo docker run --rm --pull=never --user "$GATEWAY_UID:$GATEWAY_GID" \
  --cap-drop=ALL --security-opt=no-new-privileges --read-only --pids-limit=128 \
  --cpus=2 --memory=2g --tmpfs /tmp:rw,nosuid,nodev,size=256m,mode=1777 \
  --env HOME=/tmp --env HF_HOME=/var/cache/athena-stt/hf \
  --env HF_HUB_DISABLE_TELEMETRY=1 --env HF_HUB_DISABLE_XET=1 \
  --mount "type=bind,src=$cache,dst=/var/cache/athena-stt" \
  --entrypoint /opt/athena-stt/venv/bin/python "$image" /opt/athena-stt/download_model.py
elif [ "${1:-}" = offline ]; then
 [ "${ATHENA_APPROVE_TEST:-}" = YES ] || { printf '%s\n' 'STOP: offline test approval required'; exit 2; }
 sudo docker run --rm --pull=never --network=none --user "$GATEWAY_UID:$GATEWAY_GID" \
  --cap-drop=ALL --security-opt=no-new-privileges --read-only --pids-limit=128 \
  --cpus=2 --memory=2g --tmpfs /tmp:rw,nosuid,nodev,size=256m,mode=1777 \
  --env HOME=/tmp --env EXPECTED_UID="$GATEWAY_UID" --env EXPECTED_GID="$GATEWAY_GID" \
  --env HF_HUB_OFFLINE=1 --env HF_HUB_DISABLE_TELEMETRY=1 \
  --mount "type=bind,src=$cache,dst=/var/cache/athena-stt,readonly" \
  --mount "type=bind,src=$PWD/fixtures,dst=/fixtures,readonly" \
  --entrypoint /opt/athena-stt/venv/bin/python "$image" /opt/athena-stt/selftest.py
else
 printf '%s\n' 'Usage: bash test.sh download|offline'; exit 2
fi
