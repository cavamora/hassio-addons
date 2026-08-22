from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# A4 at 150 DPI. This keeps files small while still giving CUPS/ESC/P-R
# a normal raster image to convert for the Epson printer.
PAGE_WIDTH = 1240
PAGE_HEIGHT = 1754
MARGIN = 90


def _font(size: int, *, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _save_png(img: Image.Image, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Explicit RGB PNG avoids alpha/transparency surprises in print filters.
    img.convert("RGB").save(out, format="PNG", optimize=True, dpi=(150, 150))
    return str(out)


def _draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, *, size: int = 28, fill=(0, 0, 0), bold: bool = False) -> None:
    draw.text(xy, text, font=_font(size, bold=bold), fill=fill)


def _draw_gradient(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, steps: int = 48) -> None:
    step_w = max(width // steps, 1)
    for i in range(steps):
        shade = int(255 * i / max(steps - 1, 1))
        draw.rectangle([x + i * step_w, y, x + (i + 1) * step_w, y + height], fill=(shade, shade, shade))
    draw.rectangle([x, y, x + width, y + height], outline=(0, 0, 0), width=1)


def _draw_grid(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int, spacing: int = 18) -> None:
    draw.rectangle([x, y, x + width, y + height], outline=(0, 0, 0), width=1)
    for xx in range(x, x + width + 1, spacing):
        draw.line([xx, y, xx, y + height], fill=(0, 0, 0), width=1)
    for yy in range(y, y + height + 1, spacing):
        draw.line([x, yy, x + width, yy], fill=(0, 0, 0), width=1)


def generate_maintenance_png(page_title: str, output_path: str) -> str:
    img = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _draw_text(draw, (MARGIN, 80), page_title, size=38, bold=True)
    _draw_text(draw, (MARGIN, 130), f"Generated at: {timestamp}", size=24)
    _draw_text(draw, (MARGIN, 165), "Low-ink maintenance raster image for Epson L3250", size=24)

    _draw_text(draw, (MARGIN, 240), "Ink channel blocks", size=28, bold=True)
    blocks = [
        ((0, 0, 0), "Black"),
        ((0, 180, 220), "Cyan"),
        ((220, 0, 180), "Magenta"),
        ((245, 210, 0), "Yellow"),
    ]
    y = 295
    for color, label in blocks:
        draw.rectangle([MARGIN, y, MARGIN + 300, y + 54], fill=color, outline=(0, 0, 0), width=2)
        _draw_text(draw, (MARGIN + 330, y + 10), label, size=26)
        y += 80

    _draw_text(draw, (MARGIN, 675), "Line patterns", size=28, bold=True)
    y = 730
    for width in (1, 2, 4, 7):
        draw.line([MARGIN, y, MARGIN + 500, y], fill=(0, 0, 0), width=width)
        _draw_text(draw, (MARGIN + 530, y - 15), f"{width}px", size=22)
        y += 55

    _draw_text(draw, (MARGIN, 1010), "Grid", size=28, bold=True)
    _draw_grid(draw, MARGIN, 1065, 470, 260)

    _draw_text(draw, (650, 1010), "Grayscale", size=28, bold=True)
    _draw_gradient(draw, 650, 1065, 430, 80)

    # Small color tick marks use little ink but exercise all channels.
    tick_y = 1255
    for i, color in enumerate([(0, 0, 0), (0, 180, 220), (220, 0, 180), (245, 210, 0)]):
        x = 650 + i * 105
        draw.ellipse([x, tick_y, x + 56, tick_y + 56], fill=color, outline=(0, 0, 0), width=1)

    _draw_text(draw, (MARGIN, PAGE_HEIGHT - 100), "Generated as PNG; CUPS converts through Epson ESC/P-R driver. No arbitrary files are printed.", size=19)
    return _save_png(img, output_path)


def generate_test_page_png(page_title: str, output_path: str) -> str:
    img = Image.new("RGB", (PAGE_WIDTH, PAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    _draw_text(draw, (PAGE_WIDTH // 2 - 250, 150), "Epson L3250 Test Page", size=40, bold=True)
    _draw_text(draw, (PAGE_WIDTH // 2 - 330, 215), page_title, size=24)
    _draw_text(draw, (PAGE_WIDTH // 2 - 205, 255), f"Generated at: {timestamp}", size=22)
    draw.rectangle([180, 430, PAGE_WIDTH - 180, 850], outline=(0, 0, 0), width=3)
    _draw_text(draw, (PAGE_WIDTH // 2 - 245, 620), "Basic communication and print test", size=28)
    _draw_text(draw, (MARGIN, PAGE_HEIGHT - 100), "PNG raster test. If this prints as random characters, the printer queue/filter is wrong.", size=19)

    return _save_png(img, output_path)
