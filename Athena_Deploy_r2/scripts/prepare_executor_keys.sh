#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
[[ "${1:-}" == '--apply' && "$(id -u)" == 0 ]] || exit 1
dir=/etc/athena/secrets
[[ ! -L "$dir" ]] || exit 1
install -d -m 0700 "$dir"
for f in executor_host_key executor_host_key.pub executor_client_key executor_client_key.pub executor_authorized_keys executor_known_hosts; do
  [[ ! -e "$dir/$f" && ! -L "$dir/$f" ]] || { echo 'BLOCKED: existing key material; no overwrite'; exit 1; }
done
ssh-keygen -q -t ed25519 -N '' -C athena-executor-host -f "$dir/executor_host_key"
ssh-keygen -q -t ed25519 -N '' -C athena-runtime-client -f "$dir/executor_client_key"
cp "$dir/executor_client_key.pub" "$dir/executor_authorized_keys"
printf '[executor]:2222 %s\n' "$(cut -d' ' -f1,2 "$dir/executor_host_key.pub")" > "$dir/executor_known_hosts"
chmod 0600 "$dir/executor_host_key" "$dir/executor_client_key"
chown 10000:10000 "$dir/executor_client_key"
chmod 0644 "$dir/executor_authorized_keys" "$dir/executor_known_hosts" "$dir/executor_host_key.pub" "$dir/executor_client_key.pub"
echo 'Prepared. Private keys not printed. Partial failure requires manual review.'
