#!/usr/bin/env python3
"""
Generates a minimal neofetch-style terminal SVG card (stack + socials).
Static generator — edit the DATA dict below and re-run to update.
"""

DATA = {
    "user": "tushar@github",
    "sections": [
        ("Role", "Software Engineer"),
        ("Edu", "B.Sc CSE, BRAC University '25"),
        ("", ""),
        ("Frontend", "React 19, Next.js, TypeScript, Tailwind"),
        ("Backend", "Node.js, Express, MongoDB, PostgreSQL, Redis"),
        ("Auth", "JWT, OAuth (Passport.js), Firebase Auth"),
        ("", ""),
        ("Highlights", "3 live full-stack platforms shipped"),
        ("", "Internee · Life Notes · TravelAxis"),
        ("", ""),
        ("Socials", "LinkedIn · GitHub · Email"),
    ],
}

BG = "#0d1117"
HEADER_BG = "#161b22"
GREEN = "#39d353"
CYAN = "#56d3f7"
FG = "#c9d1d9"
DIM = "#6e7681"

FONT = "'Fira Code', 'JetBrains Mono', Consolas, monospace"

def build_svg(data: dict, width: int = 560) -> str:
    line_h = 26
    top_pad = 64
    bottom_pad = 24
    n_lines = 1 + len(data["sections"]) * 1  # whoami line + section lines
    height = top_pad + n_lines * line_h + bottom_pad

    lines_svg = []
    y = top_pad

    # prompt line
    lines_svg.append(
        f'<text x="24" y="{y}" font-family="{FONT}" font-size="14">'
        f'<tspan fill="{GREEN}">{data["user"]}</tspan>'
        f'<tspan fill="{FG}"> ~ $ </tspan>'
        f'<tspan fill="{CYAN}">whoami</tspan>'
        f'</text>'
    )
    y += line_h * 1.4

    for label, value in data["sections"]:
        lines_svg.append(
            f'<text x="24" y="{y}" font-family="{FONT}" font-size="13.5">'
            f'<tspan fill="{CYAN}">{label:<12}</tspan>'
            f'<tspan fill="{FG}">{value}</tspan>'
            f'</text>'
        )
        y += line_h

    height = int(y + bottom_pad)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <clipPath id="rounded"><rect width="{width}" height="{height}" rx="10"/></clipPath>
  </defs>
  <g clip-path="url(#rounded)">
    <rect width="{width}" height="{height}" fill="{BG}"/>
    <rect width="{width}" height="34" fill="{HEADER_BG}"/>
    <circle cx="20" cy="17" r="6" fill="#ff5f56"/>
    <circle cx="40" cy="17" r="6" fill="#ffbd2e"/>
    <circle cx="60" cy="17" r="6" fill="#27c93f"/>
    <text x="{width/2}" y="21" font-family="{FONT}" font-size="12" fill="{DIM}" text-anchor="middle">{data["user"]} ~ zsh</text>
    {''.join(lines_svg)}
  </g>
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="none" stroke="#30363d"/>
</svg>'''
    return svg


if __name__ == "__main__":
    import sys
    out_path = sys.argv[1] if len(sys.argv) > 1 else "assets/neofetch-card.svg"
    svg = build_svg(DATA)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Wrote {out_path}")
