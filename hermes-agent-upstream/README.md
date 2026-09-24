# Hermes Agent Upstream — HAOS wrapper

A deliberately thin Home Assistant OS add-on wrapper around the official [`nousresearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) Docker image.

## Design

- Pins the upstream release image to `v2026.9.21`; it never clones `main` at add-on boot.
- Preserves the upstream image ENTRYPOINT, s6 supervision, profile reconciliation, and multiplex gateway lifecycle. There is no second gateway launcher or profile-start loop.
- Uses only this add-on's private `/config/.hermes` persistent state. It does not mount, read, or copy another add-on's private configuration volume.
- Keeps the upstream installation immutable and separate from persistent state.
- Provides a Home Assistant Ingress link to the official Hermes Dashboard.
- Can provide Hermes with native Home Assistant entity/service tools through the add-on's scoped Core API token, held only in the runtime environment.

## Ingress dashboard

1. In the add-on **Configuration** tab, set `dashboard_password` and optionally change `dashboard_username`.
2. Save and restart the add-on.
3. Use the Home Assistant sidebar entry / Ingress link. The add-on also exposes the authenticated dashboard directly through **Open Web UI** at `http://<Home-Assistant-host>:9119`.
4. Sign in to the Hermes Dashboard with those credentials.

Home Assistant Ingress authenticates access to Home Assistant, but the upstream dashboard also requires its own authentication when it binds outside loopback. The add-on converts the password into a hash through Hermes' supported configuration writer; it does not print or write the raw password into `/config/.hermes`. The wrapper also translates Home Assistant's Ingress base-path header for the upstream SPA so its assets and API calls remain inside the Ingress route.

If `dashboard_password` is blank, the dashboard remains disabled and the Ingress link intentionally has no backend.

## Home Assistant entities and services

`homeassistant_tools_enabled` defaults to `true`. The add-on receives a short-lived Supervisor token because it declares Home Assistant Core API access, then passes it to Hermes only through `/run` as `HASS_TOKEN` with `HASS_URL=http://supervisor/core`. It is never written to persistent `/config/.hermes` state.

This enables the native Hermes Home Assistant tools for listing entities, reading state, listing services, and calling allowed services. It does **not** enable the Supervisor API (`hassio_api` remains disabled). Set the option to `false`, save, and restart the add-on to remove the token and hide those tools.

### Interactive terminal

`dashboard_terminal` controls the Dashboard **Chat** tab. When enabled, it embeds the official Hermes TUI through a browser PTY; it is not a root shell and runs as the unprivileged `hermes` service user. The Dashboard's existing authentication remains required. Disable the toggle to remove that terminal surface.

### Browser shell

For a real shell, enable `shell_terminal_enabled` and set a non-empty `shell_terminal_username` and `shell_terminal_password` in the add-on **Configuration** page. The add-on then exposes `http://<HA-host>:7681`; it opens at `/config` with the `hermes` command on `PATH`, so run commands such as `hermes doctor`, `hermes update`, or `hermes gateway status`.

This service is **disabled by default**, runs as the unprivileged `hermes` user, and keeps the configured shell credential only in the add-on configuration plus a temporary runtime file. It is direct LAN HTTP access, so do not expose port 7681 to the internet; use VPN/Tailscale for remote access.

## Home Assistant shared folders

The add-on mounts the normal HAOS shared folders read/write:

- `/media` — Home Assistant media storage, for example `/media/MEDIA/...`.
- `/share` — Home Assistant shared storage.

Hermes file tools may read and write both paths. Other add-ons' private configuration volumes remain read-only and are not exposed as a writable share.

The add-on makes the two mount roots group-writable for the unprivileged Hermes service and applies the setgid bit so new folders inherit that group. It intentionally does not recursively change ownership or modes under existing media/shared folders.
