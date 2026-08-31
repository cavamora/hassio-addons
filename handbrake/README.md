# HandBrake Home Assistant Add-on

Home Assistant add-on wrapper around [`jlesage/handbrake`](https://github.com/jlesage/docker-handbrake) for video conversion with the full HandBrake GUI in a browser and optional watch-folder automation.

## Phase 1 scope

- HandBrake GUI through Home Assistant Ingress on internal port `5800`.
- No direct host port exposed by default.
- Raw VNC disabled.
- Web terminal disabled by default.
- Web file manager disabled by default and restricted to `/storage`, `/watch`, and `/output` when enabled.
- Upstream HandBrake state remains in the image's `/config` path; phase 1 avoids modifying Docker volume mount points at runtime.
- The add-on only mounts Home Assistant `/media`; `/share` is intentionally not mounted in phase 1.
- Conversion folders default to `/media/MEDIA/HandBrake`.
- Source files kept by default to avoid accidental data loss.

## Default folders

The wrapper configures these paths directly:

| Option | Default Home Assistant path | Purpose |
| --- | --- | --- |
| `storage_path` | `/media/MEDIA/HandBrake` | Browseable media root for manual GUI conversions. |
| `watch_path` | `/media/MEDIA/HandBrake/watch` | Drop files/folders here for automatic conversion. |
| `output_path` | `/media/MEDIA/HandBrake/output` | Converted files are written here. |

The paths can be changed in the add-on options, but must remain inside `/media`. Path traversal such as `..` is rejected at startup. The wrapper still accepts `/share` paths for future compatibility, but `/share` is not mounted by the add-on as of phase 1.

## Automatic conversion

When `automated_conversion` is enabled, files placed in `watch_path` are converted with the configured HandBrake preset and written to `output_path`.

Defaults:

- Preset: `General/Very Fast 1080p30`
- Format: `mp4`
- Keep source: `true`
- Overwrite output: `false`
- Source stable time: `30` seconds

DVD/BD sources supported by the upstream image include ISO files and folders containing `VIDEO_TS` or `BDMV`.

## Security notes

- Keep the direct `5800/tcp` port disabled unless HA Ingress fails.
- Do not enable `web_terminal` unless needed for troubleshooting.
- If enabling `web_file_manager`, it is restricted to media/watch/output paths and explicitly denied from `/config`, `/data`, `/root`, `/etc`, `/proc`, `/sys`, and `/dev`.
- This add-on can consume significant CPU. It defaults to `boot: manual` so it does not start automatically after host boot.
- The add-on does not request privileged mode or host device access in phase 1.
- The default `user_id`/`group_id` is `0:0` because Home Assistant Network Storage/CIFS media mounts can appear as `uid=0,gid=0,dir_mode=0755`; a non-root app user cannot write to those folders. Keep raw ports, VNC, and web terminal disabled when using this default. If your media path is local ext4 or mounted writable for UID 1000, you can switch back to `1000:1000`.

## First test

1. Install/start the add-on.
2. Open the HandBrake panel through Home Assistant.
3. Place a small video file in `/media/MEDIA/HandBrake/watch`.
4. Confirm the converted `.mp4` appears under `/media/MEDIA/HandBrake/output`.
5. Check add-on logs and `/config/log/hb/conversion.log` from inside the HandBrake GUI/session if needed.
