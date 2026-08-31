#!/usr/bin/env python3
"""Normalize downloaded public assets into web-ready formats.

Reads from assets/original/ and writes optimized assets to src/img/
(plus favicon + OG images). Stdlib + Pillow only.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "original"
OUT = ROOT / "src" / "img"
ICONS = ROOT / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)
ICONS.mkdir(parents=True, exist_ok=True)

NAVY = (31, 51, 88)
NAVY_DEEP = (20, 36, 63)
GOLD = (201, 169, 106)
PAPER = (250, 247, 242)
INK = (34, 48, 62)


def upscale(img, factor=2):
    w, h = img.size
    up = img.resize((w * factor, h * factor), Image.LANCZOS)
    return up.filter(ImageFilter.UnsharpMask(radius=1.6, percent=68, threshold=2))


def save(img, name, quality=86):
    path = OUT / name
    if name.endswith(".jpg"):
        img.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    elif name.endswith(".png"):
        img.save(path, "PNG", optimize=True)
    elif name.endswith(".webp"):
        img.save(path, "WEBP", quality=quality - 6, method=6)
    print(f"{name}: {path.stat().st_size // 1024} KB {img.size}")


def team_photo(src_name, out_base):
    """Crop to 4:5 keeping the top of the frame (faces), upscale to 480x600."""
    img = Image.open(SRC / src_name).convert("RGB")
    w, h = img.size
    target_ratio = 4 / 5
    new_w = min(w, int(h * target_ratio))
    new_h = int(new_w / target_ratio)
    left = (w - new_w) // 2
    top = 0  # keep top of frame
    img = img.crop((left, top, left + new_w, top + new_h))
    img = upscale(img)
    img = img.resize((480, 600), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(1.04)
    save(img, f"{out_base}.jpg")
    save(img, f"{out_base}.webp")


def building():
    img = Image.open(SRC / "building.jpg").convert("RGB")
    img = upscale(img, 2)
    save(img, "building.jpg", quality=84)
    save(img, "building.webp")


def logo():
    img = Image.open(SRC / "logo.jpg").convert("RGB")
    img = upscale(img, 2)
    save(img, "logo.png")


def logo_alpha():
    """Transparent-background logo for header use; navy text preserved."""
    img = Image.open(SRC / "logo.jpg").convert("RGB")
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    w, h = img.size
    px = img.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            chroma = mx - mn
            if mx > 228 and chroma < 26:
                alpha = 0
            elif mx > 200 and chroma < 45:
                alpha = int((228 - mx) / 28 * 255)
            else:
                alpha = 255
            opx[x, y] = (r, g, b, alpha)
    out = out.filter(ImageFilter.SMOOTH)
    # trim transparent padding so aspect ratio reflects visible content
    bbox = out.getbbox()
    if bbox:
        pad = 6
        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(out.width, bbox[2] + pad)
        bottom = min(out.height, bbox[3] + pad)
        out = out.crop((left, top, right, bottom))
    out.save(OUT / "logo-alpha.png", "PNG", optimize=True)
    print(f"logo-alpha.png: {(OUT / 'logo-alpha.png').stat().st_size // 1024} KB {out.size}")


def logo_white():
    """Footer variant: navy text knocked out to warm white, gold mark kept."""
    img = Image.open(OUT / "logo-alpha.png")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            is_gold = (r > g > b) and (r - b) > 22
            if not is_gold:
                px[x, y] = (247, 244, 238, a)
    img.save(OUT / "logo-white.png", "PNG", optimize=True)
    print(f"logo-white.png: {(OUT / 'logo-white.png').stat().st_size // 1024} KB {img.size}")


def georgia_font(size, bold=True):
    name = "Georgia Bold.ttf" if bold else "Georgia.ttf"
    return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{name}", size)


def favicon_pngs():
    for size in (512, 192, 180, 64, 32):
        s = 4 if size < 256 else 1  # draw large, downscale for crispness
        dim = size * s
        img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        radius = int(dim * 0.22)
        d.rounded_rectangle([0, 0, dim - 1, dim - 1], radius=radius, fill=GOLD + (255,))
        # subtle inner bevel line
        inset = int(dim * 0.06)
        d.rounded_rectangle(
            [inset, inset, dim - 1 - inset, dim - 1 - inset],
            radius=radius - inset, outline=(255, 255, 255, 60), width=max(1, s),
        )
        font = georgia_font(int(dim * 0.62))
        bbox = d.textbbox((0, 0), "B", font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(
            ((dim - tw) / 2 - bbox[0], (dim - th) / 2 - bbox[1]),
            "B", font=font, fill=(255, 255, 255, 255),
        )
        img = img.resize((size, size), Image.LANCZOS)
        path = ICONS / f"favicon-{size}.png"
        img.save(path, "PNG")
        print(f"{path.name}: {path.stat().st_size // 1024} KB")


def og_image():
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    # top gold band
    d.rectangle([0, 0, w, 10], fill=GOLD)
    # navy footer band
    d.rectangle([0, h - 92, w, h], fill=NAVY_DEEP)

    # logo card
    logo = Image.open(SRC / "logo.jpg").convert("RGB")
    scale = 640 / logo.width
    logo = logo.resize((640, int(logo.height * scale)), Image.LANCZOS)
    card_w, card_h = 700, logo.height + 48
    card_x, card_y = (w - card_w) // 2, 86
    d.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=18, fill=(255, 255, 255), outline=(226, 218, 205), width=2,
    )
    img.paste(logo, (card_x + (card_w - logo.width) // 2, card_y + 24))

    # tagline
    f_tag = georgia_font(40)
    tagline = "Insurance. Investments. Employee Benefits."
    bbox = d.textbbox((0, 0), tagline, font=f_tag)
    d.text(((w - bbox[2]) / 2, card_y + card_h + 40), tagline, font=f_tag, fill=INK)

    f_loc = ImageFont.truetype(
        "/System/Library/Fonts/Helvetica.ttc", 27
    )
    loc = "118 S. Main St, Princeton, Indiana  \u00b7  (812) 386-7727"
    bbox = d.textbbox((0, 0), loc, font=f_loc)
    d.text(((w - bbox[2]) / 2, card_y + card_h + 108), loc, font=f_loc, fill=(90, 100, 112))

    path = OUT / "og-image.png"
    img.save(path, "PNG", optimize=True)
    print(f"og-image.png: {path.stat().st_size // 1024} KB {img.size}")


if __name__ == "__main__":
    logo()
    logo_alpha()
    logo_white()
    team_photo("chris.jpg", "team-chris-barthel")
    team_photo("susan.jpg", "team-susan-farmer")
    team_photo("jennifer.jpg", "team-jennifer-mackay")
    building()
    favicon_pngs()
    og_image()
