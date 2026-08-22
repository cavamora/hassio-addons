from __future__ import annotations

import ipaddress
import re
import subprocess
from urllib.parse import urlparse

ALLOWED_URI_SCHEMES = {"ipp", "ipps", "socket", "lpd"}
QUEUE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")
HOSTNAME_PATTERN = re.compile(r"^[A-Za-z0-9.-]{1,253}$")
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9_./:+-]{1,256}$")
DEFAULT_EPSON_L3250_MODEL = "escpr:0/cups/model/epson-inkjet-printer-escpr/Epson-L3250_Series-epson-escpr-en.ppd"


class PrintJobError(Exception):
    pass


def _run_command(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=check, capture_output=True, text=True)


def validate_printer_queue(queue: str) -> str:
    if not queue or not QUEUE_PATTERN.fullmatch(queue):
        raise PrintJobError("Invalid printer_queue")
    return queue


def validate_printer_model(model: str) -> str:
    if not model or not MODEL_PATTERN.fullmatch(model):
        raise PrintJobError("Invalid printer_model")
    return model


def validate_printer_host(host: str) -> str:
    if not host:
        raise PrintJobError("printer_host cannot be empty when printer_uri is not provided")

    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass

    if not HOSTNAME_PATTERN.fullmatch(host) or ".." in host or host.startswith("-") or host.endswith("-"):
        raise PrintJobError("Invalid printer_host")

    return host


def validate_printer_uri(uri: str) -> str:
    if not uri:
        raise PrintJobError("Invalid empty printer_uri")

    parsed = urlparse(uri)
    if parsed.scheme not in ALLOWED_URI_SCHEMES:
        raise PrintJobError("Unsupported printer_uri scheme")

    if not parsed.netloc:
        raise PrintJobError("Invalid printer_uri")

    return uri


def build_printer_uri(printer_host: str) -> str:
    host = validate_printer_host(printer_host)
    return f"ipp://{host}/ipp/print"


def ensure_printer_queue(printer_queue: str, printer_uri: str, printer_model: str = DEFAULT_EPSON_L3250_MODEL) -> None:
    queue = validate_printer_queue(printer_queue)
    uri = validate_printer_uri(printer_uri)
    model = validate_printer_model(printer_model)

    queue_exists = _run_command(["lpstat", "-p", queue], check=False)
    if queue_exists.returncode == 0:
        return

    add_queue = _run_command(
        ["lpadmin", "-p", queue, "-E", "-v", uri, "-m", model],
        check=False,
    )
    if add_queue.returncode != 0:
        err = add_queue.stderr.strip() or add_queue.stdout.strip() or "unknown error"
        raise PrintJobError(f"Unable to create printer queue '{queue}' with model '{model}': {err}")


def print_image(image_path: str, printer_queue: str) -> None:
    queue = validate_printer_queue(printer_queue)
    send_job = _run_command(
        ["lp", "-d", queue, "-o", "fit-to-page", "-o", "media=A4", image_path],
        check=False,
    )
    if send_job.returncode != 0:
        err = send_job.stderr.strip() or send_job.stdout.strip() or "unknown error"
        raise PrintJobError(f"Unable to print image: {err}")
