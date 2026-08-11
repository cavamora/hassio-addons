#!/usr/bin/env bash
set -euo pipefail

OPTIONS=/data/options.json

read_option() {
  local key="$1"
  local default="${2:-}"
  if [[ -f "$OPTIONS" ]]; then
    jq -r --arg key "$key" --arg default "$default" 'if has($key) and .[$key] != null then .[$key] else $default end' "$OPTIONS"
  else
    printf '%s\n' "$default"
  fi
}

trim() {
  sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

read_option_trimmed() {
  read_option "$@" | trim
}

OPENVPN_PROVIDER_RAW="$(read_option_trimmed OPENVPN_PROVIDER NORDVPN)"
export OPENVPN_PROVIDER="${OPENVPN_PROVIDER_RAW^^}"
export OPENVPN_CONFIG="$(read_option_trimmed OPENVPN_CONFIG '')"
export NORDVPN_SERVER="$(read_option_trimmed NORDVPN_SERVER '')"

# Haugene's NORDVPN provider setup script ignores OPENVPN_CONFIG and instead
# selects a recommended server from the NordVPN API unless NORDVPN_SERVER is set.
# Keep the HA add-on UI backwards-compatible: if the user put a NordVPN hostname
# in OPENVPN_CONFIG, pin that hostname for the NORDVPN setup script too.
if [[ "$OPENVPN_PROVIDER" == "NORDVPN" && -z "$NORDVPN_SERVER" && "$OPENVPN_CONFIG" == *.nordvpn.com ]]; then
  export NORDVPN_SERVER="$OPENVPN_CONFIG"
fi

# Haugene downloads NordVPN configs without failing on HTTP 404, so a retired
# hostname can be saved as an HTML error page and later fail in OpenVPN with:
# "Options error ...:1: html". Detect that case before starting the upstream
# script and print a clear add-on error instead.
if [[ "$OPENVPN_PROVIDER" == "NORDVPN" && -n "$NORDVPN_SERVER" ]]; then
  NORDVPN_PROTOCOL_CHECK="${NORDVPN_PROTOCOL:-tcp}"
  if [[ "${NORDVPN_PROTOCOL_CHECK,,}" == *udp* ]]; then
    NORDVPN_PROTOCOL_CHECK="udp"
  else
    NORDVPN_PROTOCOL_CHECK="tcp"
  fi
  NORDVPN_CONFIG_URL="https://downloads.nordcdn.com/configs/files/ovpn_${NORDVPN_PROTOCOL_CHECK}/servers/${NORDVPN_SERVER}.${NORDVPN_PROTOCOL_CHECK}.ovpn"
  if ! curl -fsI --max-time 20 "$NORDVPN_CONFIG_URL" >/dev/null; then
    echo "ERROR: NordVPN OpenVPN config is not available for ${NORDVPN_SERVER} (${NORDVPN_PROTOCOL_CHECK})."
    echo "ERROR: Tried ${NORDVPN_CONFIG_URL}"
    echo "ERROR: Pick another online NordVPN server, for example br156.nordvpn.com, br160.nordvpn.com, or br161.nordvpn.com."
    exit 1
  fi
fi

export OPENVPN_USERNAME="$(read_option_trimmed OPENVPN_USERNAME '')"
export OPENVPN_PASSWORD="$(read_option OPENVPN_PASSWORD '')"
export LOCAL_NETWORK="$(read_option_trimmed LOCAL_NETWORK '192.168.0.0/16')"

# /data is the Home Assistant add-on's persistent data volume. Do not use
# /config here unless the add-on explicitly maps it; otherwise Transmission's
# resume/torrent state can be stored in the ephemeral container filesystem and
# disappear after restart/rebuild.
export TRANSMISSION_HOME="/data/transmission-home"
export TRANSMISSION_DOWNLOAD_DIR="$(read_option_trimmed TRANSMISSION_DOWNLOAD_DIR /downloads/completed)"
export TRANSMISSION_INCOMPLETE_DIR="$(read_option_trimmed TRANSMISSION_INCOMPLETE_DIR /downloads/incomplete)"
export TRANSMISSION_WATCH_DIR="$(read_option_trimmed TRANSMISSION_WATCH_DIR /downloads/watch)"
export TRANSMISSION_RPC_USERNAME="$(read_option_trimmed TRANSMISSION_RPC_USERNAME '')"
export TRANSMISSION_RPC_PASSWORD="$(read_option TRANSMISSION_RPC_PASSWORD '')"
export TRANSMISSION_RPC_PORT=9091
export TRANSMISSION_WEB_UI="$(read_option_trimmed TRANSMISSION_WEB_UI default)"

export WEBPROXY_ENABLED="$(read_option_trimmed WEBPROXY_ENABLED false)"
export WEBPROXY_PORT="$(read_option_trimmed WEBPROXY_PORT 8118)"
export TZ="$(read_option_trimmed TZ America/Sao_Paulo)"

# The HA add-on maps /dev/net/tun from the host. If Haugene tries to recreate it
# inside HAOS the mknod/rm path can fail with "Read-only file system".
export CREATE_TUN_DEVICE=false

# If a previous wrapper version managed to create /config/transmission-home in a
# persistent mount, migrate it back to /data once. In normal HAOS add-on runs,
# /config was ephemeral here and may already be gone after a container recreate.
if [[ -d /config/transmission-home && ! -e /data/transmission-home ]]; then
  echo "Migrating Transmission state from /config/transmission-home to persistent /data/transmission-home"
  mv /config/transmission-home /data/transmission-home
fi

mkdir -p "$TRANSMISSION_HOME" "$TRANSMISSION_DOWNLOAD_DIR" "$TRANSMISSION_INCOMPLETE_DIR" "$TRANSMISSION_WATCH_DIR"

echo "Starting haugene/transmission-openvpn for provider=${OPENVPN_PROVIDER}, config=${OPENVPN_CONFIG:-default}, nordvpn_server=${NORDVPN_SERVER:-auto}, local_network=${LOCAL_NETWORK}"
exec dumb-init /etc/openvpn/start.sh
