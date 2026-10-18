#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
case "${1:-}" in
 download) key=ATHENA_APPROVE_DOWNLOAD;;
 direct|integration) key=ATHENA_APPROVE_TEST;;
 *) echo 'Usage: bash test.sh download|direct|integration'; exit 2;;
esac
[ "${!key:-}" = YES ] || { echo 'STOP: separate approval required'; exit 2; }
sudo --preserve-env="$key" python3 "$PWD/control.py" "$1"
