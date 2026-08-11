# Cavamora Home Assistant Add-ons

Personal Home Assistant add-on repository for Docker-based apps packaged for HAOS.

Add this repository to Home Assistant:

```text
https://github.com/cavamora/hassio-addons
```

Home Assistant path:

```text
Settings → Add-ons → Add-on Store → ⋮ → Repositories
```

## Add-ons

### Transmission OpenVPN

Transmission BitTorrent routed through OpenVPN using the upstream [`haugene/transmission-openvpn`](https://github.com/haugene/docker-transmission-openvpn) image.

This add-on follows the local HAOS wrapper conventions:

- persistent app state under `/data`;
- explicit `/downloads`, `/share`, and `/media` mappings;
- versioned `CHANGELOG.md` for Home Assistant update notes;
- `icon.png` / `logo.png` branding;
- standard **Open Web UI** button when installed.

## Notes

This repository is for Home Assistant **add-ons**. HACS custom integrations remain in their own repositories/forks.
