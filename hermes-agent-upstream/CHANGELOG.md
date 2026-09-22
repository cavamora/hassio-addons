# Changelog

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
