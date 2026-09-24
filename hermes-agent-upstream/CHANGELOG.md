# Changelog

## 0.3.11

- Remove the completed one-time import from the former Hermes add-on and the now-unneeded `all_addon_configs:ro` mount.
- The wrapper now manages only this add-on's own persistent `/config/.hermes` state; the scoped `/media` and `/share` mounts remain unchanged.

## 0.3.10

- Update the pinned official Hermes Docker image from `v2026.9.14` to stable upstream release `v2026.9.21` (Hermes Agent `0.21.4`).
- Retain the thin HAOS wrapper, persistent-state wiring, Dashboard Ingress compatibility patch, scoped shared-folder access, and opt-in authenticated shell.

## 0.3.9

- Make the upstream Dashboard recognize Home Assistant Ingress's `X-Ingress-Path` header for SPA assets, WebSocket/API base paths, and auth redirects. This fixes the blank/404 panel caused by absolute asset URLs resolving at Home Assistant's root.

## 0.3.8

- Fix the browser shell launcher: the base image login shell reset `PATH`, hiding the Hermes CLI. The shell now opens in `/config` with `/opt/hermes/bin` available.

## 0.3.7

- Add an optional, authenticated browser shell on TCP `7681` for administrative Hermes commands such as `hermes doctor` and `hermes update`. It is disabled by default and requires an explicit username and password in add-on Configuration.

## 0.3.6

- Add a `dashboard_terminal` Configuration toggle for the authenticated interactive Hermes TUI in the Dashboard Chat tab. It defaults to enabled to preserve current behavior.

## 0.3.5

- On boot, grant the unprivileged Hermes service group write access to the HAOS `/media` and `/share` mount roots without recursively changing user media or existing shared files.

## 0.3.4

- Make the existing HAOS `media:rw` and `share:rw` mounts usable by Hermes file-writing tools, which now allow `/media` and `/share` in addition to private `/config/.hermes` state.
- Keep `all_addon_configs` strictly read-only; other add-ons' private state is not a general writable share.

## 0.3.3

- Expose the authenticated Hermes Dashboard directly on TCP port 9119, including Home Assistant's **Open Web UI** link, while retaining Ingress support.

## 0.3.2

- Set the HA add-on command to `sleep infinity`: upstream's empty Docker CMD otherwise starts its interactive CLI, which exits on HAOS's non-TTY stdin and shuts down the entire s6 gateway tree.
- Repair state ownership on every boot only when needed, so existing 0.3.0/0.3.1 imports are fixed even if an earlier migration marker exists.
- Clear the one-time update-restart obligation inherited from the old wrapper without deleting configuration or secrets.

## 0.3.1

- Normalize copied state ownership to the upstream `hermes` user before boot, fixing the imported `backups/config` permission failure.
- Omit stale update/restart obligation markers from the legacy state import so the new container does not warn about an old wrapper's already-ended gateway process.

## 0.3.0

- Migrate the old Hermes add-on's private `/config/.hermes` state into this add-on's own private volume on first boot, with a backup of provisional new-add-on state.
- Use a read-only `all_addon_configs` mount only for that one-time import; exclude the old add-on source/venv and stale runtime PID/lock files.

## 0.2.2

- Patch the exact upstream stage-2 bootstrap process so its migration child always receives `/config/.hermes` as `HERMES_HOME`; this avoids relying on s6 environment propagation between cont-init scripts.
- Stop echoing the dashboard password hash in add-on logs.

## 0.2.1

- Seed `HERMES_HOME`, `HERMES_WRITE_SAFE_ROOT`, and `HOME` into the s6 environment before upstream `01-hermes-setup` runs. This prevents its boot-time migration check from falling back to the wrong configuration scope.

## 0.2.0

- Restore the official image ENTRYPOINT rather than wrapping it with a second launcher; upstream s6 now owns the default and multiplex profile gateway lifecycle end-to-end.
- Remove the custom `profiles_to_start` loop, which attempted to start a second profile gateway and reported DIVA as missing under an incorrect home path.
- Keep `HOME=/config` aligned with `HERMES_HOME=/config/.hermes` for all upstream gateway, dashboard, and CLI subprocesses, avoiding fallback configuration drift.
- Add a secured Home Assistant Ingress link for the upstream Hermes Dashboard. It is enabled only after an add-on `dashboard_password` is configured.

## 0.1.1

- Add an explicit `profiles_to_start` boot list, defaulting to `diva`, so existing specialist profiles are registered and started through upstream Hermes lifecycle commands.

## 0.1.0

- Initial minimal HAOS wrapper around `nousresearch/hermes-agent:v2026.9.14`.
- Keeps persistent Hermes state under `/config/.hermes`.
- Delegates gateway and multi-profile supervision to the official upstream s6 lifecycle.
- Does not include a custom terminal, nginx proxy, dashboard patch, source clone, or gateway launcher.
