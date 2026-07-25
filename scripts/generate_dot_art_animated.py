#!/usr/bin/env python3
"""
Generates an ANIMATED halftone dot-art SVG: each dot starts at a random
scattered position, then flies/fades into its final position to assemble
the portrait. Plays once, then freezes (fill="freeze"), using SMIL
animations — which render correctly in GitHub READMEs via <img> tags.
"""

import argparse
import random
import sys
from PIL import Image, ImageOps


def compute_dots(rgba_img, cols, invert, total_dur, stagger_frac, seed,
                  alpha_threshold=0.4):
    """rgba_img: PIL RGBA image. Cells where the subject is transparent
    (background) are skipped entirely -> no dots, no background block."""
    rnd = random.Random(seed)
    w, h = rgba_img.size
    aspect = h / w
    rows = max(1, round(cols * aspect))

    small = rgba_img.resize((cols, rows), Image.Resampling.BOX)
    r_ch, g_ch, b_ch, a_ch = small.split()
    gray_small = Image.merge("RGB", (r_ch, g_ch, b_ch)).convert("L")
    gray_small = ImageOps.autocontrast(gray_small, cutoff=1)
    gpix = gray_small.load()
    apix = a_ch.load()

    cell = 10
    svg_w = cols * cell
    svg_h = rows * cell
    max_r = cell * 0.52

    dot_dur = round(total_dur * (1 - stagger_frac), 2)
    stagger_window = round(total_dur - dot_dur, 2)

    dots = []
    for y in range(rows):
        for x in range(cols):
            alpha = apix[x, y] / 255.0
            if alpha < alpha_threshold:
                continue  # background / transparent -> skip, no dot here

            v = gpix[x, y] / 255.0
            density = (1 - v) if not invert else v
            # inside the subject, keep a minimum visible dot even in bright
            # areas so the silhouette doesn't get patchy holes
            density = max(density, 0.22) * alpha
            if density < 0.04:
                continue
            r = round(max_r * density, 2)
            fx = x * cell + cell / 2
            fy = y * cell + cell / 2
            sx = rnd.uniform(0, svg_w)
            sy = rnd.uniform(0, svg_h)
            begin = round(rnd.uniform(0, stagger_window), 2)
            dots.append(dict(fx=fx, fy=fy, r=r, sx=sx, sy=sy, begin=begin, dur=dot_dur))

    return dots, svg_w, svg_h, dot_dur, stagger_window


def build_svg(rgba_img, cols, invert, fg, bg, total_dur, stagger_frac, seed):
    dots, svg_w, svg_h, dot_dur, stagger_window = compute_dots(
        rgba_img, cols, invert, total_dur, stagger_frac, seed
    )

    circles = []
    for d in dots:
        dx = round(d["sx"] - d["fx"], 1)
        dy = round(d["sy"] - d["fy"], 1)
        circles.append(
            f'<circle cx="{d["fx"]}" cy="{d["fy"]}" r="{d["r"]}" fill="{fg}" opacity="0">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="{dx},{dy}" to="0,0" begin="{d["begin"]}s" dur="{d["dur"]}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{d["begin"]}s" dur="{d["dur"] * 0.6}s" fill="freeze"/>'
            f'<animate attributeName="fill" values="#ffffff;{fg}" '
            f'keyTimes="0;1" begin="{d["begin"]}s" dur="{d["dur"]}s" fill="freeze"/>'
            f'</circle>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">
  <g>
    {''.join(circles)}
  </g>
</svg>'''
    return svg, dot_dur, stagger_window, len(dots)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--cols", type=int, default=70, help="Grid columns (lower = better perf)")
    ap.add_argument("--invert", action="store_true")
    ap.add_argument("--fg", default="#39d353")
    ap.add_argument("--bg", default="#0d1117")
    ap.add_argument("--crop", default=None)
    ap.add_argument("--duration", type=float, default=2.6, help="Total animation length in seconds")
    ap.add_argument("--stagger-frac", type=float, default=0.65,
                     help="Fraction of duration used for staggering dot start times (0-1)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    img = Image.open(args.input).convert("RGBA")
    img = ImageOps.exif_transpose(img)
    if args.crop:
        box = tuple(int(v) for v in args.crop.split(","))
        img = img.crop(box)

    svg, dot_dur, stagger, n = build_svg(
        img, args.cols, args.invert, args.fg, args.bg,
        args.duration, args.stagger_frac, args.seed
    )

    with open(args.output, "w") as f:
        f.write(svg)

    print(f"Wrote {args.output} | {n} dots | each flies in over {dot_dur}s | "
          f"staggered across {stagger}s | total ~{args.duration}s")


if __name__ == "__main__":
    sys.exit(main())
