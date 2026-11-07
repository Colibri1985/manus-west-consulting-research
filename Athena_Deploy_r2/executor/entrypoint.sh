#!/bin/sh
set -eu
mkdir -p /run/sshd
chmod 0755 /run/sshd
/usr/sbin/sshd -t -f /etc/ssh/sshd_config
exec /usr/sbin/sshd "$@"
