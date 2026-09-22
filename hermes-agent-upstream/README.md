# Hermes Agent Upstream — HAOS wrapper

A deliberately thin Home Assistant OS add-on wrapper around the official [`nousresearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) Docker image.

## Design

- Pins the upstream release image to `v2026.9.14`; it never clones `main` at add-on boot.
- Uses the official image's s6 supervision and profile lifecycle.
- Uses `/config/.hermes` as `HERMES_HOME`, preserving existing configuration, profiles, skills, sessions, cron jobs, auth state, and logs.
- Keeps the upstream installation immutable. It does not reuse `/config/.hermes/hermes-agent/`, which belongs to the older third-party add-on.
- Exposes no web UI or API port in this first phase. Messaging gateways are the supported interface.
- Starts profiles listed in the HA add-on `profiles_to_start` setting. The default is `diva`.

## Migration test

1. Make a backup of `/config/.hermes`.
2. Stop the old Hermes add-on. Two live gateways must never share the same Hermes state directory or Discord/Telegram credentials.
3. Install this add-on from the same repository.
4. Start it and inspect its logs for the default gateway and `DIVA` Discord connection.
5. Test DIVA in Discord before uninstalling the old add-on.

The existing `.env` files remain the source of credentials. Home Assistant-specific secrets stored only in the old add-on options must be migrated separately before the old add-on is removed.
