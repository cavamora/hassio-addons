# Epson Maintenance Print (Home Assistant Add-on)

Home Assistant add-on to generate and print a periodic maintenance page for Epson L3250.

## What it does

- Exposes a local HTTP API on port `8099` (mapped from container `8080`)
- Generates `/share/epson-maintenance/maintenance.png`
- Prints PNG raster images through CUPS using the Epson ESC/P-R L3250 driver, without external cloud services
- Supports `dry_run` mode

See `DOCS.md` for full setup and automation examples.
