# Home Assistant add-on wrapper around jlesage/handbrake.
# Upstream project: https://github.com/jlesage/docker-handbrake
FROM jlesage/handbrake:latest

RUN apk add --no-cache jq \
    && mkdir -p /usr/local/bin

COPY rootfs/ /
RUN chmod +x /usr/local/bin/ha-handbrake-wrapper.sh

ENTRYPOINT ["/usr/local/bin/ha-handbrake-wrapper.sh"]
