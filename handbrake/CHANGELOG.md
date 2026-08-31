# Changelog

## 0.1.0

- Initial phase-1 Home Assistant add-on wrapper around `jlesage/handbrake`.
- Add HandBrake GUI through Home Assistant Ingress.
- Add safe watch/output folder defaults under `/media/MEDIA/HandBrake`.
- Disable raw VNC and web terminal by default.
- Keep source files by default and reject path traversal outside `/media` or `/share`.
