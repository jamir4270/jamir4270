"""Generate the profile README SVGs (light + dark) from one palette.

Run:  python scripts/build_assets.py          -> writes assets/*.svg from assets/src/*.jpg
      python scripts/build_assets.py --shoot  -> re-screenshots the live apps first (needs Edge + Pillow)

Rule of the design: the aero look (sky, bubbles, haze) lives only in the hero.
Everything below it is flat, flush to the text edge, and shows the real product.
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT, SRC = ROOT / "assets", ROOT / "assets" / "src"
W = 840
# shortcut: system font stack instead of outlined text (Segoe UI can't be redistributed as paths)
FONT = "'Segoe UI', 'Frutiger', 'Helvetica Neue', 'Noto Sans', Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Code', Consolas, 'SF Mono', monospace"

THEMES = {
    "light": dict(sky="#CFE6EC", mist="#EEF5F2", field="#8DB596", aqua="#8CCFD6", text="#2F4A3E",
                  muted="#5E7A70", rule="#C9D9D3", surface="#F6FAF8", node="#FFFFFF", gloss=0.45),
    "dark": dict(sky="#16302F", mist="#0F1E1F", field="#5E8F72", aqua="#4FA3AC", text="#E3F0EC",
                 muted="#9DB5AE", rule="#2C4644", surface="#132625", node="#1A3332", gloss=0.10),
}
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, label, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" font-family="{FONT}">'
            f"<title>{escape(label)}</title><style>{css}{REDUCED}</style>{body}</svg>")


def lines(x, y, rows, size, fill, lh):
    return "".join(f'<text x="{x}" y="{y + i * lh:.0f}" font-size="{size}" fill="{fill}">{escape(r)}</text>'
                   for i, r in enumerate(rows))


# ---------- hero: the one aero moment ----------
def hero(t):
    h = 230
    bubbles = "".join(
        f'<circle class="b" cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)" stroke="#FFFFFF" stroke-opacity=".7" '
        f'style="animation-duration:{d}s;animation-delay:-{dl}s"/>'
        for cx, cy, r, d, dl in [(90, 200, 14, 26, 3), (180, 225, 7, 20, 11), (560, 215, 18, 32, 8),
                                 (640, 235, 9, 22, 15), (720, 205, 12, 28, 1), (780, 230, 6, 18, 6),
                                 (470, 240, 8, 24, 19), (300, 235, 5, 19, 9)])
    body = f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['sky']}"/><stop offset="1" stop-color="{t['mist']}"/></linearGradient>
<linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="{t['gloss']}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<radialGradient id="orb" cx=".35" cy=".3" r=".75"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/>
  <stop offset=".35" stop-color="{t['aqua']}" stop-opacity=".55"/><stop offset="1" stop-color="{t['field']}" stop-opacity=".35"/></radialGradient>
<clipPath id="clip"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{h}" fill="url(#sky)"/>
  <path class="f1" d="M-40 185 C 120 160, 260 195, 420 175 S 700 155, 880 180 V 240 H -40 Z" fill="{t['field']}" fill-opacity=".35"/>
  <path class="f2" d="M-40 205 C 150 185, 330 215, 520 195 S 760 190, 880 205 V 240 H -40 Z" fill="{t['field']}" fill-opacity=".5"/>
  {bubbles}
  <rect width="{W}" height="{h * 0.48:.0f}" fill="url(#gloss)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="#FFFFFF" stroke-opacity=".6"/>
<text x="40" y="88" font-size="44" font-weight="300" letter-spacing=".5" fill="{t['text']}">Jamir Oasis Andrade</text>
<text x="42" y="120" font-size="17" fill="{t['text']}">Full-stack web developer · digitizing traditional workflows</text>
<text x="42" y="146" font-size="13.5" fill="{t['muted']}">Freelance  ·  Veris backend  ·  GCI World cohort  ·  DOST scholar  ·  CS at VSU</text>"""
    css = """
.b{animation:rise linear infinite}
@keyframes rise{0%{transform:translate(0,0);opacity:0}12%{opacity:.9}50%{transform:translate(8px,-100px)}
88%{opacity:.8}100%{transform:translate(-6px,-210px);opacity:0}}
.f1{animation:drift 30s ease-in-out infinite alternate}
.f2{animation:drift 22s ease-in-out infinite alternate-reverse}
@keyframes drift{from{transform:translateX(-14px)}to{transform:translateX(14px)}}"""
    return svg(W, h, body, "Jamir Oasis Andrade, full-stack web developer", css)


# ---------- project cards: flat, real picture, plain facts ----------
def photo(slug, x, y, w, h):
    b64 = base64.b64encode((SRC / f"{slug}.jpg").read_bytes()).decode()
    return (f'<image href="data:image/jpeg;base64,{b64}" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'preserveAspectRatio="xMidYMid slice"/>')


def frame(t, w, h, inner, label):
    body = f"""<clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{t['surface']}"/>{inner}</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="none" stroke="{t['rule']}"/>"""
    return svg(w, h, body, label)


def text_block(t, x, y, p, title_size, desc_size):
    lh = desc_size * 1.55
    dy = y + title_size + 38
    return (f'<text x="{x}" y="{y}" font-size="11" font-weight="600" letter-spacing="1.4" fill="{t["muted"]}">{escape(p["status"])}</text>'
            f'<text x="{x}" y="{y + title_size + 12}" font-size="{title_size}" font-weight="600" fill="{t["text"]}">{escape(p["title"])}</text>'
            + lines(x, dy, p["desc"], desc_size, t["text"], lh)
            + f'<text x="{x}" y="{dy + len(p["desc"]) * lh + 12:.0f}" font-size="12.5" fill="{t["muted"]}">{escape(p["stack"])}</text>')


def label(p):
    return f'{p["title"]}. {" ".join(p["desc"])} Built with {p["stack"].replace("  ·  ", ", ")}.'


def lead_card(t, p):
    w, h, iw = W, 300, 440
    inner = (photo(p["slug"], 0, 0, iw, h) + f'<line x1="{iw}" y1="0" x2="{iw}" y2="{h}" stroke="{t["rule"]}"/>'
             + text_block(t, iw + 36, 70, p, 26, 14))
    return frame(t, w, h, inner, label(p))


def pair_card(t, p, picture, side):
    """Half-width card; `side` puts an 8px gutter on the inner edge so two at width=50% meet the outer edges."""
    w, h, ih, gut = 412, 450, 250, 8
    inner = (picture + f'<line x1="0" y1="{ih}" x2="{w}" y2="{ih}" stroke="{t["rule"]}"/>'
             + text_block(t, 28, ih + 34, p, 20, 13.5))
    card = frame(t, w, h, inner, label(p))
    x = gut if side == "right" else 0
    return card.replace(f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"',
                        f'width="{w + gut}" height="{h}" viewBox="{-x} 0 {w + gut} {h}"', 1)


def florence_schema(t, w=412, h=250):
    """Still diagram of Project Florence's real foreign keys (docs/database/schema.dbml)."""
    cx = [22, 118, 214, 310]          # four columns, 80 wide, 16 gap
    ry = [44, 100, 156]               # three lanes
    nw, nh = 80, 28
    nodes = {"events": (0, 0), "attendance": (1, 0), "obligations": (2, 0), "payments": (3, 0),
             "endorsements": (0, 1), "merits": (1, 1), "demerits": (2, 1), "receipts": (3, 1),
             "sessions": (0, 2), "participants": (1, 2), "credits": (2, 2), "refunds": (3, 2)}
    edges = [("events", "attendance"), ("attendance", "obligations"), ("payments", "obligations"),
             ("endorsements", "merits"), ("attendance", "demerits"), ("payments", "receipts"),
             ("receipts", "refunds"), ("sessions", "participants"), ("participants", "credits")]
    out = [f'<rect width="{w}" height="{h}" fill="{t["mist"]}"/>',
           f'<text x="22" y="28" font-family="{MONO}" font-size="10.5" fill="{t["muted"]}">public schema · 31 tables · Postgres</text>']
    for a, b in edges:
        (ac, ar), (bc, br) = nodes[a], nodes[b]
        if ar == br:  # same lane: side to side
            l, r = sorted((ac, bc))
            x1, x2, y = cx[l] + nw, cx[r], ry[ar] + nh / 2
            out.append(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{t["muted"]}" stroke-opacity=".7"/>')
        elif ac == bc:  # same column: top to bottom
            x, y1, y2 = cx[ac] + nw / 2, ry[min(ar, br)] + nh, ry[max(ar, br)]
            out.append(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{t["muted"]}" stroke-opacity=".7"/>')
        else:  # elbow: out of the bottom of a, into the side of b
            x1, y1 = cx[ac] + nw / 2 + 14, ry[ar] + nh
            y2 = ry[br] + nh / 2
            out.append(f'<path d="M{x1} {y1} V{y2} H{cx[bc]}" fill="none" stroke="{t["muted"]}" stroke-opacity=".7"/>')
    for k, (c, r) in nodes.items():
        out.append(f'<rect x="{cx[c]}" y="{ry[r]}" width="{nw}" height="{nh}" rx="5" fill="{t["node"]}" stroke="{t["rule"]}"/>'
                   f'<text x="{cx[c] + nw / 2}" y="{ry[r] + 18}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="10.5" fill="{t["text"]}">{k}</text>')
    by = 208
    out.append(f'<rect x="22" y="{by}" width="{cx[3] + nw - 22}" height="{nh}" rx="5" fill="none" stroke="{t["field"]}" stroke-dasharray="4 3"/>'
               f'<text x="{w / 2}" y="{by + 18}" text-anchor="middle" font-family="{MONO}" font-size="10.5" '
               f'fill="{t["text"]}">clearances · council → academic → RLE</text>')
    return "".join(out)


def stack(t):
    rows = [("Web", "Next.js · React · TypeScript · Tailwind CSS · Supabase · PostgreSQL · Vercel"),
            ("Backend", "C# · ASP.NET MVC · Node.js · Firebase"),
            ("Mobile", "Flutter · Dart"),
            ("Data and AI", "Python · RAG pipelines · local LLMs · agentic SWE · C / C++")]
    rh = 44
    h = len(rows) * rh + 1
    body = [f'<line x1="0" y1=".5" x2="{W}" y2=".5" stroke="{t["rule"]}"/>']
    for i, (k, v) in enumerate(rows):
        y = i * rh
        body.append(f'<text x="0" y="{y + 28}" font-size="12" font-weight="600" letter-spacing="1.2" fill="{t["muted"]}">{escape(k.upper())}</text>'
                    f'<text x="150" y="{y + 28}" font-size="14.5" fill="{t["text"]}">{escape(v)}</text>'
                    f'<line x1="0" y1="{y + rh + .5}" x2="{W}" y2="{y + rh + .5}" stroke="{t["rule"]}"/>')
    return svg(W, h, "".join(body), "Tech stack. " + "; ".join(f"{k}: {v}" for k, v in rows))


def wave(t):
    h = 60
    p = ("M0 34 C 105 18, 210 50, 315 34 S 525 18, 630 34 S 840 50, 945 34 S 1155 18, 1260 34 "
         "S 1470 50, 1575 34 S 1785 18, 1890 34 V 60 H 0 Z")
    body = (f'<path class="w1" d="{p}" fill="{t["aqua"]}" fill-opacity=".22"/>'
            f'<path class="w2" d="{p}" fill="{t["field"]}" fill-opacity=".28" transform="translate(0 8)"/>')
    css = """.w1{animation:flow 28s linear infinite}.w2{animation:flow 40s linear infinite reverse}
@keyframes flow{from{transform:translateX(0)}to{transform:translateX(-630px)}}"""
    return svg(W, h, body, "decorative wave", css)


PROJECTS = {
    "oreo": dict(slug="oreo", status="LIVE  ·  OREO-FINANCE.VERCEL.APP", title="Oreo Finance",
                 desc=["Tracks income, expenses and transfers across",
                       "every account and currency you hold, converted",
                       "to one base currency with rates cached for a day."],
                 stack="Next.js 16  ·  React 19  ·  Supabase  ·  Tailwind CSS",
                 url="https://oreo-finance.vercel.app", crop=(700, 135, 1300, 525)),
    "florence": dict(slug="florence", status="IN DEVELOPMENT", title="Project Florence",
                     desc=["Nursing faculty records in one place: events,",
                           "fines, payments, merits, demerits, service",
                           "hours and semester clearance."],
                     stack="Next.js 16  ·  PostgreSQL  ·  Supabase Auth  ·  R2"),
    "ncs": dict(slug="ncs", status="LIVE  ·  COURSE FINAL PROJECT", title="VSU Nursing Conduct System",
                desc=["Merit and demerit records for nursing students,",
                      "logged by faculty, reviewed by admins, emailed",
                      "to the student when filed."],
                stack="Next.js 16  ·  Supabase  ·  shadcn/ui  ·  Nodemailer",
                url="https://batch-2025-vsu-ncs-web.vercel.app", crop=(730, 180, 1360, 580)),
}


def shoot():
    from PIL import Image
    # shortcut: hard-coded Windows Edge path; swap for chrome/chromium elsewhere
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    SRC.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS.values():
        if "url" not in p:
            continue
        png = Path(tempfile.gettempdir()) / f"shot-{p['slug']}.png"
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1440,900",
                        "--force-device-scale-factor=2", "--virtual-time-budget=8000",
                        f"--screenshot={png}", p["url"]], check=True, capture_output=True, timeout=120)
        im = Image.open(png).convert("RGB").crop(tuple(v * 2 for v in p["crop"]))
        im.thumbnail((900, 900))  # about 2x of the largest frame it fills
        im.save(SRC / f"{p['slug']}.jpg", quality=80, optimize=True, progressive=True)
        print("shot", p["slug"], im.size, (SRC / f"{p['slug']}.jpg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    if "--shoot" in sys.argv:
        shoot()
    for f in OUT.glob("*.svg"):
        f.unlink()  # drop files from older layouts
    for mode, t in THEMES.items():
        files = {
            "hero": hero(t), "stack": stack(t), "wave": wave(t),
            "card-oreo": lead_card(t, PROJECTS["oreo"]),
            "card-florence": pair_card(t, PROJECTS["florence"], florence_schema(t), "left"),
            "card-ncs": pair_card(t, PROJECTS["ncs"], photo("ncs", 0, 0, 412, 250), "right"),
        }
        for name, s in files.items():
            (OUT / f"{name}-{mode}.svg").write_text(s, encoding="utf-8")
    import xml.dom.minidom as md  # self-check: every file is well-formed XML
    for f in OUT.glob("*.svg"):
        md.parse(str(f))
    print(f"ok: {len(list(OUT.glob('*.svg')))} svgs,", sum(f.stat().st_size for f in OUT.glob('*.svg')) // 1024, "KB total")
