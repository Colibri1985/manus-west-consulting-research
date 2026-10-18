#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
[ "${ATHENA_APPROVE_SWITCH:-}" = YES ] || { echo 'STOP: separate approval required'; exit 2; }
sudo --preserve-env=ATHENA_APPROVE_SWITCH,ATHENA_FOURTH_COMPOSE_REVIEWED,BACKUP_DIR python3 "$PWD/control.py" rollback
