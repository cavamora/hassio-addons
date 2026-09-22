# Hermes Agent Upstream — HAOS wrapper

A deliberately thin Home Assistant OS add-on wrapper around the official [`nousresearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) Docker image.

## Design

- Pins the upstream release image to `v2026.9.14`; it never clones `main` at add-on boot.
- Preserves the upstream image ENTRYPOINT, s6 supervision, profile reconciliation, and multiplex gateway lifecycle. There is no second gateway launcher or profile-start loop.
- Uses `/config/.hermes` as `HERMES_HOME`, preserving existing configuration, profiles, skills, sessions, cron jobs, auth state, and logs.
- Aligns `HOME=/config` with `HERMES_HOME=/config/.hermes` for upstream subprocesses that fall back to `$HOME/.hermes`; this prevents them from creating a second, empty Hermes configuration tree.
- Keeps the upstream installation immutable. It does not reuse `/config/.hermes/hermes-agent/`, which belongs to the older third-party add-on.
- Provides a Home Assistant Ingress link to the official Hermes Dashboard.

## Ingress dashboard

1. In the add-on **Configuration** tab, set `dashboard_password` and optionally change `dashboard_username`.
2. Save and restart the add-on.
3. Use **Open Web UI** / the add-on information-page link.
4. Sign in to the Hermes Dashboard with those credentials.

Home Assistant Ingress authenticates access to Home Assistant, but the upstream dashboard also requires its own authentication when it binds outside loopback. The add-on converts the password into a bcrypt hash through Hermes' supported configuration writer; it does not print or write the raw password into `/config/.hermes`.

If `dashboard_password` is blank, the dashboard remains disabled and the Ingress link intentionally has no backend.

## Migration test

1. Make a backup of `/config/.hermes`.
2. Stop the old Hermes add-on. Two live gateways must never share the same Hermes state directory or Discord/Telegram credentials.
3. Install this add-on from the same repository.
4. Configure the dashboard password if you want the Ingress UI, then start it.
5. Inspect the logs for the multiplex gateway and platform connections.
6. Test Telegram and DIVA in Discord before uninstalling the old add-on.

The existing `.env` files remain the source of credentials. Home Assistant-specific secrets stored only in the old add-on options must be migrated separately before the old add-on is removed.
