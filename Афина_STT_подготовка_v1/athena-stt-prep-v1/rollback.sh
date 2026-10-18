#!/usr/bin/env bash
set -euo pipefail
[ "${ATHENA_APPROVE_SWITCH:-}" = YES ] || { echo 'STOP: rollback approval required'; exit 2; }
: "${BACKUP_DIR:?Use the SAME transaction directory as switch}"
cd -- "$(dirname -- "$0")"
# Restore config first; old image must never be started with local_command config
# while its override providing the command is absent.
sudo env ATHENA_APPROVE_SWITCH=YES python3 "$PWD/config_transaction.py" restore --backup "$BACKUP_DIR"
sudo docker compose \
 -f /srv/hermes-agent/compose.telegram.yaml \
 -f /srv/hermes-agent/compose.telegram.workspace.yaml \
 -f /srv/hermes-agent/compose.telegram.executor.yaml \
 up -d --no-deps --no-build --pull never --force-recreate gateway
sudo docker inspect --format 'IMAGE={{.Image}} STATUS={{.State.Status}}' hermes-telegram-gateway-1
echo 'Verify old digest and configuration checksum. Images and model cache are not deleted.'
