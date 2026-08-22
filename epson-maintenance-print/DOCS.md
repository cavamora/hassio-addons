# Epson Maintenance Print Add-on Docs

## Installation

1. In Home Assistant, open **Settings → Add-ons → Add-on Store**.
2. Add this repository URL as an add-on repository:
   `https://github.com/cavamora/epson-maintenance-print`
3. Install **Epson Maintenance Print** and start it.

## Configuration

Configure the add-on options:

- `printer_host`: printer fixed IP/hostname (recommend DHCP reservation). Default: `192.168.88.116`.
- `printer_queue`: CUPS queue name to use/create.
- `printer_uri`: optional explicit URI. If empty, uses `ipp://<printer_host>/ipp/print`.
- `printer_model`: CUPS model/PPD. Default is the Epson ESC/P-R L3250 model:
  `escpr:0/cups/model/epson-inkjet-printer-escpr/Epson-L3250_Series-epson-escpr-en.ppd`
- `page_title`: title printed on the maintenance page.
- `dry_run`: generate PNG but do not print.
- `debug`: include traceback in API error responses.

The add-on generates a PNG raster image, then prints through CUPS using the Epson ESC/P-R driver. This avoids sending raw PDF bytes to the printer.

Example `printer_uri` alternatives:

- IPP (default construction): `ipp://192.168.88.116/ipp/print`
- Raw socket: `socket://192.168.88.116:9100`

## API endpoints

- `GET /` - status, effective config, and endpoint list
- `GET /health` - returns `{ "ok": true }`
- `POST /print/maintenance` - generate/reuse maintenance PNG and print
- `POST /print/test` - generate and print a short PNG test page

## Quick checks

Health check:

```bash
curl -s http://homeassistant.local:8099/health
```

Maintenance print trigger:

```bash
curl -X POST http://homeassistant.local:8099/print/maintenance
```

## Home Assistant integration

```yaml
rest_command:
  epson_l3250_print_maintenance:
    url: "http://homeassistant.local:8099/print/maintenance"
    method: POST
    timeout: 60
```

```yaml
input_datetime:
  epson_l3250_ultima_manutencao:
    name: Epson L3250 última manutenção
    has_date: true
    has_time: true
```

```yaml
alias: Epson L3250 - manutenção a cada 10 dias
mode: single
trigger:
  - platform: time
    at: "10:00:00"
condition:
  - condition: template
    value_template: >
      {% set last = states('input_datetime.epson_l3250_ultima_manutencao') %}
      {% if last in ['unknown', 'unavailable', 'none', ''] %}
        true
      {% else %}
        {{ (now() - as_datetime(last)).days >= 10 }}
      {% endif %}
action:
  - service: rest_command.epson_l3250_print_maintenance
  - delay: "00:00:10"
  - service: input_datetime.set_datetime
    target:
      entity_id: input_datetime.epson_l3250_ultima_manutencao
    data:
      datetime: "{{ now().strftime('%Y-%m-%d %H:%M:%S') }}"
  - service: notify.mobile_app_iphone
    data:
      title: "Epson L3250"
      message: "Página de manutenção enviada para impressão."
```
