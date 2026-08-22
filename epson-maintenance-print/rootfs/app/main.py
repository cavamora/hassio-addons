from __future__ import annotations

import json
import os
import traceback
from dataclasses import dataclass
from pathlib import Path

from flask import Flask, jsonify

from generate_test_page import generate_maintenance_png, generate_test_page_png
from print_job import (
    DEFAULT_EPSON_L3250_MODEL,
    build_printer_uri,
    ensure_printer_queue,
    print_image,
    validate_printer_uri,
)

SHARE_DIR = Path("/share/epson-maintenance")
MAINTENANCE_FILE = SHARE_DIR / "maintenance.png"
TEST_FILE = SHARE_DIR / "test.png"


@dataclass
class AppConfig:
    printer_host: str
    printer_queue: str
    printer_uri: str
    printer_model: str
    page_title: str
    dry_run: bool
    debug: bool


def _load_options() -> AppConfig:
    defaults = {
        "printer_host": "192.168.88.116",
        "printer_queue": "epson_l3250",
        "printer_uri": "",
        "printer_model": DEFAULT_EPSON_L3250_MODEL,
        "page_title": "Epson L3250 - manutenção automática",
        "dry_run": False,
        "debug": False,
    }

    options_path = Path("/data/options.json")
    options: dict[str, object] = {}
    if options_path.exists():
        with options_path.open("r", encoding="utf-8") as fh:
            options = json.load(fh)

    merged = {**defaults, **options}
    return AppConfig(
        printer_host=str(merged.get("printer_host", defaults["printer_host"])),
        printer_queue=str(merged.get("printer_queue", defaults["printer_queue"])),
        printer_uri=str(merged.get("printer_uri", defaults["printer_uri"])),
        printer_model=str(merged.get("printer_model", defaults["printer_model"])),
        page_title=str(merged.get("page_title", defaults["page_title"])),
        dry_run=bool(merged.get("dry_run", defaults["dry_run"])),
        debug=bool(merged.get("debug", defaults["debug"])),
    )


def _current_printer_uri(config: AppConfig) -> str:
    if config.printer_uri:
        return validate_printer_uri(config.printer_uri)
    return build_printer_uri(config.printer_host)


def _error_response(summary: str, exc: Exception, debug: bool):
    payload = {"ok": False, "error": summary}
    if debug:
        payload["error_type"] = exc.__class__.__name__
        payload["traceback"] = traceback.format_exc()
    return jsonify(payload), 500


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        config = _load_options()
        return jsonify(
            {
                "ok": True,
                "name": "epson-maintenance-print",
                "endpoints": ["/", "/health", "/print/maintenance", "/print/test"],
                "config": {
                    "printer_host": config.printer_host,
                    "printer_queue": config.printer_queue,
                    "printer_uri": config.printer_uri,
                    "printer_model": config.printer_model,
                    "page_title": config.page_title,
                    "dry_run": config.dry_run,
                    "debug": config.debug,
                },
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/print/maintenance")
    def print_maintenance():
        config = _load_options()

        try:
            file_path = generate_maintenance_png(config.page_title, str(MAINTENANCE_FILE))

            if config.dry_run:
                return jsonify(
                    {
                        "ok": True,
                        "dry_run": True,
                        "message": "Dry run: PNG generated but not printed",
                        "file": file_path,
                    }
                )

            uri = _current_printer_uri(config)
            ensure_printer_queue(config.printer_queue, uri, config.printer_model)
            print_image(file_path, config.printer_queue)

            return jsonify(
                {
                    "ok": True,
                    "message": "Maintenance PNG sent to printer",
                    "file": file_path,
                    "printer_queue": config.printer_queue,
                }
            )
        except Exception as exc:  # noqa: BLE001
            if config.debug:
                app.logger.error(traceback.format_exc())
            return _error_response("Maintenance print failed", exc, config.debug)

    @app.post("/print/test")
    def print_test():
        config = _load_options()

        try:
            file_path = generate_test_page_png(config.page_title, str(TEST_FILE))

            if config.dry_run:
                return jsonify(
                    {
                        "ok": True,
                        "dry_run": True,
                        "message": "Dry run: Test PNG generated but not printed",
                        "file": file_path,
                    }
                )

            uri = _current_printer_uri(config)
            ensure_printer_queue(config.printer_queue, uri, config.printer_model)
            print_image(file_path, config.printer_queue)

            return jsonify(
                {
                    "ok": True,
                    "message": "Test PNG sent to printer",
                    "file": file_path,
                    "printer_queue": config.printer_queue,
                }
            )
        except Exception as exc:  # noqa: BLE001
            if config.debug:
                app.logger.error(traceback.format_exc())
            return _error_response("Test print failed", exc, config.debug)

    return app


if __name__ == "__main__":
    app = create_app()
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=8080, debug=debug)
