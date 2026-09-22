# Changelog

## 0.1.1

- Add an explicit `profiles_to_start` boot list, defaulting to `diva`, so existing specialist profiles are registered and started through upstream Hermes lifecycle commands.

## 0.1.0

- Initial minimal HAOS wrapper around `nousresearch/hermes-agent:v2026.9.14`.
- Keeps persistent Hermes state under `/config/.hermes`.
- Delegates gateway and multi-profile supervision to the official upstream s6 lifecycle.
- Does not include a custom terminal, nginx proxy, dashboard patch, source clone, or gateway launcher.
