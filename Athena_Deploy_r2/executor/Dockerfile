ARG UBUNTU_BASE
FROM ${UBUNTU_BASE}
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends openssh-server openssh-client python3 ca-certificates bash coreutils tar gzip unzip git openssl \
    && useradd --uid 10000 --create-home --shell /bin/bash runner \
    && usermod --password "$(openssl passwd -6 "$(openssl rand -hex 32)")" runner \
    && mkdir -p /etc/athena /run/sshd /workspace /inputs \
    && chown 10000:10000 /workspace \
    && rm -f /etc/ssh/ssh_host_* \
    && rm -rf /var/lib/apt/lists/*
COPY --chmod=0555 entrypoint.sh /usr/local/bin/executor-entrypoint
EXPOSE 2222
ENTRYPOINT ["/usr/local/bin/executor-entrypoint"]
CMD ["-D","-e","-f","/etc/ssh/sshd_config"]
