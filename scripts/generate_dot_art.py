#!/usr/bin/env python3
"""
Generate a halftone / dot-art SVG portrait from a source photo.
Used to recreate the "ASCII-style dotted portrait" effect seen in
GitHub profile README banners.

Usage:
    python3 generate_dot_art.py <input_image> <output_svg> [--cols N] [--dark]

The image is:
  1. Converted to grayscale
  2. Optionally auto-cropped/centered on the face-ish region (simple center-crop)
  3. Downsampled to a grid of COLS x ROWS cells
  4. Each cell becomes a circle whose radius is proportional to brightness
     (darker pixel = bigger dot, like ink density in a halftone print)
  5. Rendered as a single scalable SVG using currentColor / CSS vars so it
     matches light & dark GitHub themes automatically.
"""

import argparse
import sys
from PIL import Image, ImageOps


def build_svg(gray_img: Image.Image, cols: int, invert: bool, fg: str, bg: str) -> str:
    w, h = gray_img.size
    aspect = h / w
    rows = max(1, round(cols * aspect))

    # Downsample using box filter for smooth averaging per-cell
    small = gray_img.resize((cols, rows), Image.Resampling.BOX)
    pixels = small.load()

    cell = 10  # px per grid cell in the output SVG coordinate space
    svg_w = cols * cell
    svg_h = rows * cell
    max_r = cell * 0.52

    circles = []
    for y in range(rows):
        for x in range(cols):
            v = pixels[x, y] / 255.0  # 0 = black, 1 = white
            density = (1 - v) if not invert else v
            if density < 0.04:
                continue  # skip near-blank cells for a lighter/cleaner look
            r = round(max_r * density, 2)
            cx = x * cell + cell / 2
            cy = y * cell + cell / 2
            circles.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <rect width="100%" height="100%" fill="{bg}"/>
  <g fill="{fg}">
    {''.join(circles)}
  </g>
</svg>'''
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--cols", type=int, default=90, help="Grid columns (detail level)")
    ap.add_argument("--invert", action="store_true", help="Invert brightness mapping")
    ap.add_argument("--fg", default="#39d353", help="Dot color (default GitHub green)")
    ap.add_argument("--bg", default="#0d1117", help="Background color (default GitHub dark)")
    ap.add_argument("--crop", default=None,
                     help="Optional crop box 'left,top,right,bottom' in pixels")
    args = ap.parse_args()

    img = Image.open(args.input).convert("RGB")
    img = ImageOps.exif_transpose(img)

    if args.crop:
        box = tuple(int(v) for v in args.crop.split(","))
        img = img.crop(box)

    gray = ImageOps.autocontrast(img.convert("L"), cutoff=1)

    svg = build_svg(gray, args.cols, args.invert, args.fg, args.bg)

    with open(args.output, "w") as f:
        f.write(svg)

    print(f"Wrote {args.output} ({args.cols} cols)")


if __name__ == "__main__":
    sys.exit(main())
