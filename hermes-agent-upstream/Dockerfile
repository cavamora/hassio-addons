# Thin HAOS wrapper around the official Hermes image. Upstream retains ownership
# of s6, gateway supervision, profile reconciliation, and all Hermes services.
FROM nousresearch/hermes-agent:v2026.9.21

# HA add-on data is persisted at /config/.hermes.  Keep HOME aligned with that
# root for the few upstream subprocesses which fall back to $HOME/.hermes when
# HERMES_HOME is not available in their service environment.
ENV HERMES_HOME=/config/.hermes \
    HERMES_WRITE_SAFE_ROOT=/config/.hermes:/media:/share
RUN sed -i \
        -e 's|export HOME=/opt/data|export HOME=/config|' \
        -e 's|HERMES_HOME="${HERMES_HOME:-/opt/data}"|HERMES_HOME="/config/.hermes"\nexport HERMES_HOME\nexport HERMES_WRITE_SAFE_ROOT="/config/.hermes:/media:/share"\nexport HOME="/config"|' \
        /opt/hermes/docker/main-wrapper.sh \
        /opt/hermes/docker/hermes-exec-shim.sh \
        /opt/hermes/docker/stage2-hook.sh \
        /etc/s6-overlay/s6-rc.d/dashboard/run \
    && grep -F 'export HOME=/config' /opt/hermes/docker/main-wrapper.sh \
    && grep -F 'export HOME=/config' /opt/hermes/docker/hermes-exec-shim.sh \
    && grep -F 'HERMES_HOME="/config/.hermes"' /opt/hermes/docker/stage2-hook.sh \
    && grep -F 'export HOME=/config' /etc/s6-overlay/s6-rc.d/dashboard/run \
    && sed -i 's|_DASHBOARD_EMBEDDED_CHAT_ENABLED = True|_DASHBOARD_EMBEDDED_CHAT_ENABLED = os.getenv("HERMES_DASHBOARD_EMBEDDED_CHAT_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}|' /opt/hermes/hermes_cli/web_server.py \
    && grep -F 'HERMES_DASHBOARD_EMBEDDED_CHAT_ENABLED' /opt/hermes/hermes_cli/web_server.py

# Optional browser shell, pinned to an upstream ttyd release and verified per
# architecture. It runs only when the add-on's shell_terminal_enabled option is
# explicitly enabled with a non-empty password.
RUN arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) asset=x86_64; sha256=8a217c968aba172e0dbf3f34447218dc015bc4d5e59bf51db2f2cd12b7be4f55 ;; \
      arm64) asset=aarch64; sha256=b38acadd89d1d396a0f5649aa52c539edbad07f4bc7348b27b4f4b7219dd4165 ;; \
      *) echo "Unsupported ttyd architecture: $arch" >&2; exit 1 ;; \
    esac; \
    curl -fsSL --retry 3 -o /usr/local/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.$asset"; \
    echo "$sha256  /usr/local/bin/ttyd" | sha256sum -c -; \
    chmod 0755 /usr/local/bin/ttyd; \
    /usr/local/bin/ttyd --version

# Home Assistant Ingress forwards its dynamic base route in X-Ingress-Path,
# while the upstream dashboard only recognizes X-Forwarded-Prefix. Teach both
# SPA asset rewriting and authenticated redirect handling to accept HA's header.
RUN sed -i 's|request.headers.get("x-forwarded-prefix")|request.headers.get("x-forwarded-prefix") or request.headers.get("x-ingress-path")|g' \
        /opt/hermes/hermes_cli/web_server_dashboard.py \
        /opt/hermes/hermes_cli/dashboard_auth/prefix.py \
    && grep -F 'request.headers.get("x-ingress-path")' /opt/hermes/hermes_cli/web_server_dashboard.py \
    && grep -F 'request.headers.get("x-ingress-path")' /opt/hermes/hermes_cli/dashboard_auth/prefix.py

COPY rootfs/ /
RUN chmod 0755 \
        /etc/cont-init.d/00-ha-hermes-home \
        /etc/cont-init.d/90-ha-dashboard-auth \
        /etc/services.d/hermes-shell-terminal/run \
        /usr/local/bin/hermes-browser-shell

# HA Add-ons start an image with its default command. The upstream image's empty
# CMD launches an interactive CLI, which exits immediately without a TTY and
# tears down s6 plus every gateway. Keep its ENTRYPOINT/lifecycle intact but use
# its documented long-lived no-op command; upstream profile reconciliation owns
# the actual gateway services.
CMD ["sleep", "infinity"]
