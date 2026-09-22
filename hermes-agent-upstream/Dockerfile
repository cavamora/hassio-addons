# Minimal HAOS wrapper. The official image owns Hermes, s6, profile lifecycle,
# gateway supervision, dependencies, and upgrades.
FROM nousresearch/hermes-agent:v2026.9.14

# Home Assistant exposes the add-on configuration mount at /config. Keep the
# existing Hermes state there rather than creating a second private data store.
# The upstream wrapper otherwise hard-codes HOME=/opt/data for tool subprocesses;
# make it follow HERMES_HOME without altering Hermes runtime behavior.
RUN sed -i 's|export HOME=/opt/data|export HOME="${HERMES_HOME}/home"|' /opt/hermes/docker/main-wrapper.sh \
    && grep -F 'export HOME="${HERMES_HOME}/home"' /opt/hermes/docker/main-wrapper.sh

COPY rootfs/ /
RUN chmod 0755 /usr/local/bin/ha-hermes-upstream /etc/cont-init.d/90-ha-start-profiles

ENTRYPOINT ["/usr/local/bin/ha-hermes-upstream"]
