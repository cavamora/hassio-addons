#!/usr/bin/env sh
set -eu

OPTIONS=/data/options.json

read_option() {
  key="$1"
  default="${2:-}"
  if [ -f "$OPTIONS" ]; then
    jq -r --arg key "$key" --arg default "$default" \
      'if has($key) and .[$key] != null then .[$key] else $default end' "$OPTIONS"
  else
    printf '%s\n' "$default"
  fi
}

read_bool_as_int() {
  key="$1"
  default="${2:-false}"
  if [ -f "$OPTIONS" ]; then
    jq -r --arg key "$key" --argjson default "$default" \
      'if has($key) and .[$key] != null then (if .[$key] then "1" else "0" end) else (if $default then "1" else "0" end) end' "$OPTIONS"
  else
    if [ "$default" = "true" ]; then printf '1\n'; else printf '0\n'; fi
  fi
}

trim() {
  sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

safe_path_option() {
  key="$1"
  default="$2"
  value="$(read_option "$key" "$default" | trim)"

  # Security: only expose Supervisor-provided media/share mounts to the GUI and
  # converter. Reject traversal rather than attempting to normalize it.
  case "$value" in
    *..*|*'//'*)
      echo "ERROR: ${key} must not contain '..' or duplicate slashes: ${value}" >&2
      exit 1
      ;;
  esac

  case "$value" in
    /media|/media/*|/share|/share/*)
      printf '%s\n' "$value"
      ;;
    *)
      echo "ERROR: ${key} must be inside /media or /share, got: ${value}" >&2
      exit 1
      ;;
  esac
}

export TZ="$(read_option TZ America/Sao_Paulo | trim)"
export USER_ID="$(read_option user_id 1000 | trim)"
export GROUP_ID="$(read_option group_id 1000 | trim)"

STORAGE_PATH="$(safe_path_option storage_path /media/MEDIA/HandBrake)"
WATCH_PATH="$(safe_path_option watch_path /media/MEDIA/HandBrake/watch)"
OUTPUT_PATH="$(safe_path_option output_path /media/MEDIA/HandBrake/output)"

# Do not replace /config, /storage, /watch or /output with symlinks. The
# upstream image declares some of these as Docker volumes, so they can be mount
# points at runtime and removing them fails with "Resource busy". Use the real
# Supervisor-provided /media or /share paths directly instead.
mkdir -p "$WATCH_PATH" "$OUTPUT_PATH"

# Best effort for normal ext4 folders. CIFS mounts created by Home Assistant
# Network Storage may ignore chown/chmod and stay uid=0 mode=0755; in that case
# the configured USER_ID must be 0 to write there.
chown "$USER_ID:$GROUP_ID" "$WATCH_PATH" "$OUTPUT_PATH" 2>/dev/null || true
chmod u+rwx "$WATCH_PATH" "$OUTPUT_PATH" 2>/dev/null || true

export HANDBRAKE_GUI=1
export HANDBRAKE_DEBUG="$(read_bool_as_int debug false)"
export HANDBRAKE_GUI_QUEUE_STARTUP_ACTION=NONE

export AUTOMATED_CONVERSION="$(read_bool_as_int automated_conversion true)"
export AUTOMATED_CONVERSION_PRESET="$(read_option preset 'General/Very Fast 1080p30' | trim)"
export AUTOMATED_CONVERSION_FORMAT="$(read_option format mp4 | trim)"
export AUTOMATED_CONVERSION_KEEP_SOURCE="$(read_bool_as_int keep_source true)"
export AUTOMATED_CONVERSION_OVERWRITE_OUTPUT="$(read_bool_as_int overwrite_output false)"
export AUTOMATED_CONVERSION_SOURCE_STABLE_TIME="$(read_option source_stable_time 30 | trim)"
export AUTOMATED_CONVERSION_SOURCE_MIN_DURATION="$(read_option source_min_duration 10 | trim)"
export AUTOMATED_CONVERSION_WATCH_DIR="$WATCH_PATH"
export AUTOMATED_CONVERSION_OUTPUT_DIR="$OUTPUT_PATH"
OUTPUT_SUBDIR="$(read_option output_subdir '' | trim)"
if [ -n "$OUTPUT_SUBDIR" ]; then
  case "$OUTPUT_SUBDIR" in
    /*|*..*)
      echo "ERROR: output_subdir must be relative and must not contain '..': ${OUTPUT_SUBDIR}" >&2
      exit 1
      ;;
  esac
  export AUTOMATED_CONVERSION_OUTPUT_SUBDIR="$OUTPUT_SUBDIR"
fi

export WEB_FILE_MANAGER="$(read_bool_as_int web_file_manager false)"
export WEB_FILE_MANAGER_ALLOWED_PATHS="${STORAGE_PATH},${WATCH_PATH},${OUTPUT_PATH}"
export WEB_FILE_MANAGER_DENIED_PATHS=/config,/data,/root,/etc,/proc,/sys,/dev
export WEB_TERMINAL="$(read_bool_as_int web_terminal false)"
export WEB_AUDIO="$(read_bool_as_int web_audio false)"
export WEB_NOTIFICATION=0
export WEB_AUTHENTICATION=0
export SECURE_CONNECTION=0

# Security: HA Ingress handles browser access. Do not expose raw VNC internally.
export VNC_LISTENING_PORT=-1

if [ "$WEB_TERMINAL" = "1" ]; then
  echo "WARNING: web_terminal is enabled. Keep the add-on reachable only through trusted HA Ingress/direct LAN access." >&2
fi

cat <<EOF
Starting HandBrake add-on
  storage_path=${STORAGE_PATH}
  watch_path=${WATCH_PATH}
  output_path=${OUTPUT_PATH}
  automated_conversion=${AUTOMATED_CONVERSION}
  preset=${AUTOMATED_CONVERSION_PRESET}
  keep_source=${AUTOMATED_CONVERSION_KEEP_SOURCE}
  web_file_manager=${WEB_FILE_MANAGER}
  web_terminal=${WEB_TERMINAL}
  vnc=disabled
EOF

exec /init
