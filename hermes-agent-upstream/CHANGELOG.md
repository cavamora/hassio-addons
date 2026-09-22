# Changelog

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
