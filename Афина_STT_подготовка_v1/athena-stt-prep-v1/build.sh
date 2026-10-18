#!/usr/bin/env bash
set -euo pipefail
[ "${ATHENA_APPROVE_BUILD:-}" = YES ] || { printf '%s\n' 'STOP: build approval required'; exit 2; }
cd -- "$(dirname -- "$0")"
base='nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784'
user=$(sudo docker image inspect --format '{{if .Config.User}}{{.Config.User}}{{else}}0:0{{end}}' "$base")
# No secret build args, no host networking, no production bind mounts.
sudo docker build --pull=false --build-arg "BASE_RUNTIME_USER=$user" \
 -t athena-hermes-stt:fw1.2.1-av16.1.0-v1 ./build-context
