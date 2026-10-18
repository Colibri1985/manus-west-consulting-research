FROM nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784
# Restored to the BASE IMAGE user, supplied by preflight. Not guessed from executor.
ARG BASE_RUNTIME_USER
USER root
WORKDIR /opt/hermes
COPY requirements.lock /opt/athena-stt/requirements.lock
# Isolated venv: no replacing packages in Hermes dependency generations.
RUN /opt/hermes/.venv/bin/python -m venv /opt/athena-stt/venv \
 && /opt/athena-stt/venv/bin/python -m pip install --disable-pip-version-check --no-cache-dir \
      --only-binary=:all: --require-hashes -r /opt/athena-stt/requirements.lock \
 && /opt/athena-stt/venv/bin/python -m pip check
COPY versions.json transcribe.py download_model.py selftest.py /opt/athena-stt/
RUN test -n "$BASE_RUNTIME_USER" \
 && /opt/athena-stt/venv/bin/python -c "import av,ctranslate2,onnxruntime,faster_whisper; assert av.__version__=='16.1.0'" \
 && chmod -R a-w /opt/athena-stt
# Parent ENTRYPOINT and CMD remain inherited. Only tests override entrypoint.
USER ${BASE_RUNTIME_USER}
