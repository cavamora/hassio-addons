# Home Assistant add-on wrapper around the upstream Haugene image.
# Upstream project: https://github.com/haugene/docker-transmission-openvpn
FROM haugene/transmission-openvpn:latest

COPY rootfs/ /
RUN chmod +x /usr/local/bin/ha-addon-wrapper.sh

CMD ["/usr/local/bin/ha-addon-wrapper.sh"]
