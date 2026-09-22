# Thin HAOS wrapper around the official Hermes image. Upstream retains ownership
# of s6, gateway supervision, profile reconciliation, and all Hermes services.
FROM nousresearch/hermes-agent:v2026.9.14

# HA add-on data is persisted at /config/.hermes.  Keep HOME aligned with that
# root for the few upstream subprocesses which fall back to $HOME/.hermes when
# HERMES_HOME is not available in their service environment.
ENV HERMES_HOME=/config/.hermes \
    HERMES_WRITE_SAFE_ROOT=/config/.hermes
RUN sed -i \
        -e 's|export HOME=/opt/data|export HOME=/config|' \
        -e 's|HERMES_HOME="${HERMES_HOME:-/opt/data}"|HERMES_HOME="/config/.hermes"\nexport HERMES_HOME\nexport HERMES_WRITE_SAFE_ROOT="/config/.hermes"\nexport HOME="/config"|' \
        /opt/hermes/docker/main-wrapper.sh \
        /opt/hermes/docker/hermes-exec-shim.sh \
        /opt/hermes/docker/stage2-hook.sh \
        /etc/s6-overlay/s6-rc.d/dashboard/run \
    && grep -F 'export HOME=/config' /opt/hermes/docker/main-wrapper.sh \
    && grep -F 'export HOME=/config' /opt/hermes/docker/hermes-exec-shim.sh \
    && grep -F 'HERMES_HOME="/config/.hermes"' /opt/hermes/docker/stage2-hook.sh \
    && grep -F 'export HOME=/config' /etc/s6-overlay/s6-rc.d/dashboard/run

COPY rootfs/ /
RUN chmod 0755 \
        /etc/cont-init.d/00-ha-hermes-home \
        /etc/cont-init.d/90-ha-dashboard-auth

# Preserve the official image ENTRYPOINT and empty CMD.  In particular, do not
# wrap it with a second launcher: entrypoint-dispatch.sh must be PID 1 so the
# upstream s6 lifecycle can register and supervise the multiplex gateway.
