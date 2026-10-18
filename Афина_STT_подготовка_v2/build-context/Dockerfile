FROM nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784
ARG BASE_RUNTIME_USER
ARG ATHENA_BUILD_DIGEST
USER root
WORKDIR /opt/hermes
COPY requirements.lock /opt/athena-stt/requirements.lock
RUN /opt/hermes/.venv/bin/python -m venv /opt/athena-stt/venv \
 && /opt/athena-stt/venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir \
    --only-binary=:all: --require-hashes -r /opt/athena-stt/requirements.lock \
 && /opt/athena-stt/venv/bin/python -m pip check
COPY versions.json contract-hashes.json transcribe.py download_model.py selftest.py integration_test.py /opt/athena-stt/
RUN test -n "$BASE_RUNTIME_USER" && test -n "$ATHENA_BUILD_DIGEST" \
 && /opt/athena-stt/venv/bin/python -c "import av,ctranslate2,onnxruntime,faster_whisper; assert av.__version__=='16.1.0'" \
 && chmod -R a-w /opt/athena-stt
LABEL org.athena.stt.build-digest=$ATHENA_BUILD_DIGEST
USER ${BASE_RUNTIME_USER}
