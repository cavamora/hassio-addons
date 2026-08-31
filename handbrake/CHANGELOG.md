# Changelog

## 0.1.4

- Remove the `/share` add-on mount for a narrower security boundary; phase 1 only needs `/media`.
- Narrow the default GUI/manual storage path from `/media` to `/media/MEDIA/HandBrake`.

## 0.1.3

- Default HandBrake runtime user/group to `0:0` so the automatic converter can write to Home Assistant CIFS media mounts that are exposed as `uid=0,gid=0,dir_mode=0755`.
- Add best-effort startup `chown`/`chmod` for local `/media` or `/share` folders while tolerating CIFS mounts that ignore ownership changes.

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
