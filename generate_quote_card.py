#!/usr/bin/env python3
"""
generate_quote_card.py
Fetches today's quote from zenquotes.io and writes assets/quote-card.svg.

Usage:
  python generate_quote_card.py           # fetch live quote
  python generate_quote_card.py --dry-run # use fallback quote (for local testing)
"""

import os, sys, json, textwrap, urllib.request, urllib.error

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

FALLBACK_QUOTE  = "First, solve the problem. Then, write the code."
FALLBACK_AUTHOR = "John Johnson"

W    = 820   # canvas width
PAD  = 48    # left/right content inset
INDENT = PAD


# ── helpers ──────────────────────────────────────────────────────────────────

def xe(s: str) -> str:
    """XML-escape a string."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def fetch_quote() -> tuple[str, str]:
    try:
        req = urllib.request.Request(
            "https://zenquotes.io/api/today",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())[0]
            return data["q"].strip(), data["a"].strip()
    except Exception as ex:
        print(f"  [warn] Could not fetch quote ({ex}), using fallback.")
        return FALLBACK_QUOTE, FALLBACK_AUTHOR


def wrap(text: str, width: int = 68) -> list[str]:
    """Wrap text to fit inside W - 2*PAD at ~13px/char for font-size 16."""
    return textwrap.wrap(text, width=width) or [text]


# ── SVG generator ─────────────────────────────────────────────────────────────

def generate(quote: str, author: str) -> None:
    lines = wrap(quote)

    LINE_H        = 28
    PAD_TOP       = 72
    FOOTER_H      = 36
    PAD_BOT       = FOOTER_H + 50
    H = PAD_TOP + len(lines) * LINE_H + PAD_BOT

    quote_mark_y  = PAD_TOP - 6
    first_line_y  = PAD_TOP + 10
    attr_y        = first_line_y + len(lines) * LINE_H + 30
    divline_y     = attr_y - 12
    close_mark_y  = H - FOOTER_H - 14
    footer_y      = H - FOOTER_H
    footer_mid_y  = footer_y + FOOTER_H // 2

    text_lines = "\n".join(
        f'  <text class="qt" x="{INDENT}" y="{first_line_y + i * LINE_H}"'
        f' fill="#e6edf3" font-size="16">{xe(l)}</text>'
        for i, l in enumerate(lines)
    )

    svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"   stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#001a0a"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stop-color="#00FF41"/>
      <stop offset="100%" stop-color="#00994d"/>
    </linearGradient>
    <linearGradient id="aline" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#00FF41"/>
      <stop offset="100%" stop-color="#7ee787"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .qt  {{ font-family:"JetBrains Mono","Courier New",monospace; font-weight:500; }}
      .sans{{ font-family:system-ui,sans-serif; }}
      .mono{{ font-family:"JetBrains Mono","Courier New",monospace; }}

      @keyframes fi    {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
      @keyframes fi2   {{ from{{opacity:0}} to{{opacity:1}} }}
      @keyframes pulse {{ 0%,100%{{opacity:.65}} 50%{{opacity:1}} }}
      @keyframes shim  {{
        0%   {{ transform:translateX(-100%); }}
        100% {{ transform:translateX(200%); }}
      }}

      .r0  {{ opacity:0; animation:fi  .55s ease  .2s both; }}
      .r1  {{ opacity:0; animation:fi  .55s ease  .5s both; }}
      .r2  {{ opacity:0; animation:fi  .55s ease  .9s both; }}
      .r3  {{ opacity:0; animation:fi2 .7s  ease 1.4s both; }}
      .r4  {{ opacity:0; animation:fi2 .7s  ease 1.9s both; }}
      .bar {{ animation:pulse 3s ease-in-out infinite; }}

      .shim-wrap {{ overflow:hidden; }}
      .shim {{
        animation:shim 3.5s ease-in-out 0.5s infinite;
        fill:url(#shimgrad);
      }}
    </style>
    <linearGradient id="shimgrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"   stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%"  stop-color="#ffffff" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card-clip">
      <rect width="{W}" height="{H}" rx="10" ry="10"/>
    </clipPath>
  </defs>

  <!-- background -->
  <rect width="{W}" height="{H}" rx="10" ry="10"
        fill="url(#bg)" stroke="#003320" stroke-width="1.5"/>

  <!-- shimmer -->
  <g clip-path="url(#card-clip)">
    <rect class="shim" x="0" y="0" width="60%" height="{H}" opacity="1"/>
  </g>

  <!-- left accent bar -->
  <rect class="bar" x="0" y="0" width="5" height="{H}"
        rx="2.5" ry="2.5" fill="url(#bar)"/>

  <!-- opening quote mark -->
  <text class="r0 sans" x="{INDENT - 4}" y="{quote_mark_y}"
        fill="#00FF41" font-size="68" font-weight="900"
        opacity="0.18" filter="url(#glow)">"</text>

  <!-- quote text lines -->
  <g class="r1">
{text_lines}
  </g>

  <!-- divider + attribution -->
  <g class="r2">
    <line x1="{INDENT}" y1="{divline_y}" x2="{INDENT + 90}" y2="{divline_y}"
          stroke="url(#aline)" stroke-width="1.5"/>
    <text class="sans" x="{INDENT + 100}" y="{attr_y - 2}"
          fill="#7ee787" font-size="14" font-weight="600">
      &#x2014;&#x2002;{xe(author)}
    </text>
  </g>

  <!-- closing quote mark -->
  <text class="r3 sans" x="{W - INDENT - 28}" y="{close_mark_y}"
        fill="#00994d" font-size="68" font-weight="900"
        text-anchor="end" opacity="0.14" filter="url(#glow)">"</text>

  <!-- footer block -->
  <g class="r4">
    <line x1="0" y1="{footer_y}" x2="{W}" y2="{footer_y}"
          stroke="#003320" stroke-width="1"/>
    <g clip-path="url(#card-clip)">
      <rect x="0" y="{footer_y}" width="{W}" height="{FOOTER_H}"
            fill="#0d1117" opacity="0.85"/>
      <rect x="0" y="{footer_y}" width="5" height="{FOOTER_H}"
            fill="url(#bar)"/>
    </g>
    <!-- pulsing dot -->
    <circle cx="{INDENT + 12}" cy="{footer_mid_y}" r="4"
            fill="#00FF41" opacity="0.9">
      <animate attributeName="r" values="3.5;5;3.5" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.9;0.5;0.9" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text class="mono" x="{INDENT + 24}" y="{footer_mid_y + 5}"
          fill="#00FF41" font-size="12" font-weight="700"
          letter-spacing="0.5">Dev Quote of the Day</text>
  </g>
</svg>"""

    out = os.path.join(ASSETS_DIR, "quote-card.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[ok] quote-card.svg ({len(lines)} line(s), H={H}px, author: {author})")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    if dry:
        q, a = FALLBACK_QUOTE, FALLBACK_AUTHOR
        print(f"[dry-run] Using fallback quote.")
    else:
        print("Fetching today's quote from zenquotes.io …")
        q, a = fetch_quote()

    print(f'  Quote : {q[:70]}{"…" if len(q) > 70 else ""}')
    print(f'  Author: {a}')
    generate(q, a)
