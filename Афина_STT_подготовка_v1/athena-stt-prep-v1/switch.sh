#!/usr/bin/env bash
set -euo pipefail
[ "${ATHENA_APPROVE_SWITCH:-}" = YES ] || { echo 'STOP: separate switch approval required'; exit 2; }
: "${BACKUP_DIR:?Set new backup dir under /srv/hermes-agent/athena-stt-backups}"
cd -- "$(dirname -- "$0")"
common=(-f /srv/hermes-agent/compose.telegram.yaml -f /srv/hermes-agent/compose.telegram.workspace.yaml -f /srv/hermes-agent/compose.telegram.executor.yaml)
# Fail before touching config if image or merged Compose is invalid.
sudo docker image inspect athena-hermes-stt:fw1.2.1-av16.1.0-v1 --format '{{.Id}}'
sudo docker compose "${common[@]}" -f "$PWD/compose.telegram.stt.yaml" config --quiet
sudo env ATHENA_APPROVE_SWITCH=YES python3 "$PWD/config_transaction.py" apply --backup "$BACKUP_DIR"
if ! sudo docker compose "${common[@]}" -f "$PWD/compose.telegram.stt.yaml" up -d --no-deps --no-build --pull never --force-recreate gateway; then
 echo 'SWITCH FAILED: use rollback.sh with the same BACKUP_DIR; no success is claimed'; exit 1
fi
sudo docker inspect --format 'IMAGE={{.Image}} STATUS={{.State.Status}}' hermes-telegram-gateway-1
echo 'RUNNING is not voice acceptance. Check new voice and restart persistence separately.'
