# Changelog

## 0.1.2

- Fix startup on HAOS by not replacing upstream `/config`, `/storage`, `/watch`, or `/output` paths with symlinks; some are Docker volume mount points and cannot be removed at runtime.
- Point automatic conversion directly at the configured `/media` or `/share` paths instead.

## 0.1.1

- Fix HAOS build by not switching to the named `root` user in the upstream image; BuildKit runs as UID 0 by default, while the upstream image lacks a passwd entry named `root`.

## 0.1.0

- Initial phase-1 Home Assistant add-on wrapper around `jlesage/handbrake`.
- Add HandBrake GUI through Home Assistant Ingress.
- Add safe watch/output folder defaults under `/media/MEDIA/HandBrake`.
- Disable raw VNC and web terminal by default.
- Keep source files by default and reject path traversal outside `/media` or `/share`.
