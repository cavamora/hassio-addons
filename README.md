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

### Epson Maintenance Print

Generates a low-ink PNG maintenance page and prints it to an Epson L3250 through CUPS using the Epson ESC/P-R driver. Default printer IP: `192.168.88.116`.

Use this to periodically exercise black/cyan/magenta/yellow channels without Epson Cloud or external services.

### Transmission OpenVPN

Transmission BitTorrent routed through OpenVPN using the upstream [`haugene/transmission-openvpn`](https://github.com/haugene/docker-transmission-openvpn) image.

This repository follows the local HAOS wrapper conventions:

- persistent app state under `/data` where relevant;
- explicit mount mappings when an add-on needs `/downloads`, `/share`, or `/media`;
- versioned `CHANGELOG.md` for Home Assistant update notes;
- standard **Open Web UI** button when installed.

## Notes

This repository is for Home Assistant **add-ons**. HACS custom integrations remain in their own repositories/forks.
