#!/usr/bin/env python3
"""Generate launcher icons for every RU manga extension in one unified style.

Style: 192px canvas (xxxhdpi), rounded square inset 5px, radius 44,
accent-coloured 5px border, near-black tinted fill, big bold accent monogram.
All mipmap densities are derived from the 432px master by downscaling.

Usage: python3 .github/scripts/make-icons.py [ext ...]
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(__file__).resolve().parents[2] / "src" / "ru"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# density -> icon side in px
DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}

MASTER = 768  # render big, downscale for clean edges
SCALE = MASTER / 192

# ext dir -> (monogram, accent rgb, dark fill rgb)
ICONS = {
    "acomics": ("AC", (255, 150, 60), (34, 24, 14)),
    "allhentai": ("AH", (255, 70, 110), (36, 16, 24)),
    "astramanga": ("AM", (140, 130, 255), (22, 22, 40)),
    "comx": ("CX", (255, 90, 80), (36, 18, 18)),
    "desu": ("DS", (120, 210, 255), (14, 28, 40)),
    "henchan": ("HC", (255, 100, 150), (36, 16, 26)),
    "hentailib": ("HL", (235, 90, 160), (34, 16, 28)),
    "inkstory": ("IS", (160, 200, 255), (18, 24, 38)),
    "mangabuff": ("MB", (255, 180, 70), (36, 26, 14)),
    "mangachan": ("MC", (120, 220, 140), (16, 32, 22)),
    "mangahub": ("MH", (90, 190, 240), (14, 26, 38)),
    "mangalib": ("ML", (110, 90, 245), (22, 22, 34)),
    "mangamen": ("MM", (200, 170, 255), (26, 20, 38)),
    "mangapoisk": ("MP", (100, 210, 200), (14, 30, 32)),
    "mangashi": ("MS", (255, 140, 120), (36, 20, 20)),
    "mintmanga": ("MT", (80, 225, 175), (14, 32, 28)),
    "ninegrid": ("9G", (150, 220, 90), (22, 32, 16)),
    "nudemoon": ("NM", (230, 120, 200), (32, 16, 30)),
    "puremanga": ("PM", (170, 225, 255), (16, 26, 36)),
    "readmanga": ("RM", (255, 120, 90), (36, 20, 18)),
    "seimanga": ("SM", (120, 200, 255), (16, 26, 40)),
    "selfmanga": ("SF", (255, 200, 90), (36, 28, 14)),
    "senkognito": ("SK", (190, 130, 255), (28, 18, 38)),
    "senkuro": ("SN", (90, 215, 190), (14, 32, 30)),
    "slashlib": ("SL", (255, 110, 170), (36, 16, 28)),
    "tomilolib": ("TL", (255, 160, 120), (36, 24, 18)),
    "unicomics": ("UC", (255, 220, 90), (36, 32, 14)),
    "usagi": ("US", (255, 170, 190), (36, 22, 26)),
    "wamanga": ("WM", (130, 180, 255), (18, 24, 40)),
    "yagamiproject": ("YP", (200, 220, 120), (28, 32, 16)),
    "yaoichan": ("YC", (245, 100, 180), (34, 16, 28)),
}


def fit_font(text: str, max_w: int, max_h: int) -> ImageFont.FreeTypeFont:
    size = max_h
    while size > 8:
        font = ImageFont.truetype(FONT, size)
        box = font.getbbox(text)
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return font
        size -= 2
    return ImageFont.truetype(FONT, 8)


def render(monogram: str, accent, fill) -> Image.Image:
    img = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    inset = round(5 * SCALE)
    radius = round(44 * SCALE)
    border = round(5 * SCALE)
    box = (inset, inset, MASTER - inset - 1, MASTER - inset - 1)

    draw.rounded_rectangle(box, radius=radius, fill=(*accent, 255))
    draw.rounded_rectangle(
        (box[0] + border, box[1] + border, box[2] - border, box[3] - border),
        radius=radius - border,
        fill=(*fill, 255),
    )

    inner = MASTER - 2 * (inset + border)
    font = fit_font(monogram, int(inner * 0.80), int(inner * 0.52))
    left, top, right, bottom = font.getbbox(monogram)
    draw.text(
        (MASTER / 2 - (left + right) / 2, MASTER / 2 - (top + bottom) / 2),
        monogram,
        font=font,
        fill=(*accent, 255),
    )
    return img


def main(only=None):
    for ext, (monogram, accent, fill) in ICONS.items():
        if only and ext not in only:
            continue
        master = render(monogram, accent, fill)
        for density, side in DENSITIES.items():
            out = SRC / ext / "res" / f"mipmap-{density}" / "ic_launcher.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            master.resize((side, side), Image.LANCZOS).save(out)
        print(f"{ext}: {monogram}")


if __name__ == "__main__":
    import sys

    main(set(sys.argv[1:]) or None)
