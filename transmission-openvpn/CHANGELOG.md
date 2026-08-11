# Changelog

## 1.0.12

- Move the add-on metadata URL to the umbrella Home Assistant add-ons repository: `cavamora/hassio-addons`.
- No configuration or data migration is required when switching repositories because the add-on slug remains `transmission_openvpn`.

## 1.0.11

- Use Transmission's built-in default web UI by default and automatically fall back to it when old saved options request `transmission-web-control`. This avoids broken add-torrent/path behavior such as `undefined` download locations with the current upstream image.

## 1.0.10

- Downgrade NordVPN setup ICMP ping failures to warnings after the wrapper has already validated the exact `.ovpn` download URL with HTTPS. This avoids false startup failures on HAOS when `downloads.nordcdn.com` is reachable by curl but not ping.

## 1.0.9

- Add the standard Home Assistant add-on Web UI link for Transmission at port `9091`, so the add-on dashboard can show an **Open Web UI** action.

## 1.0.8

- Store Transmission state under the Home Assistant add-on persistent `/data/transmission-home` path so torrent lists, resume data, and settings survive add-on restarts/rebuilds.
- Stop moving `/data/transmission-home` out of the way; for HAOS add-ons, `/data` is the correct persistent storage location.

## 1.0.7

- Change the default NordVPN server from retired `br125.nordvpn.com` to currently available `br156.nordvpn.com`.
- Add a preflight check for pinned NordVPN server config downloads, so retired hosts fail with a clear add-on error instead of OpenVPN parsing an HTML 404 page.

## 1.0.6

- Replace the add-on logo with a compact transparent version so Home Assistant does not crop/truncate the artwork in update cards.

## 1.0.5

- Add a custom Transmission + VPN icon/logo for Home Assistant add-on listings.
- Add this changelog so Home Assistant can show update release notes.

## 1.0.4

- Mount Home Assistant `/media` into the add-on with read/write access.
- This allows Transmission paths such as `/media/MEDIA/Download` to use the real Home Assistant media share instead of an internal container directory.

## 1.0.3

- Pin NordVPN servers correctly by mapping a NordVPN hostname from `OPENVPN_CONFIG` to `NORDVPN_SERVER`.
- Keeps existing add-on UI configuration compatible while preventing Haugene's NordVPN setup from choosing a different recommended server automatically.

## 1.0.2

- Trim add-on option values before exporting them to Haugene environment variables.
- Migrate/fix Transmission home handling so Haugene keeps using `/config/transmission-home` instead of falling back to deprecated `/data/transmission-home`.

## 1.0.1

- Fix HAOS TUN handling by using the host-provided `/dev/net/tun` and disabling TUN recreation inside the container.

## 1.0.0

- Initial Home Assistant add-on wrapper around `haugene/transmission-openvpn`.
