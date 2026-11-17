"""Generate the profile README SVGs (light + dark) from one palette.

Run:  python scripts/build_assets.py          -> writes assets/*.svg from assets/src/*.jpg
      python scripts/build_assets.py --shoot  -> re-screenshots the live apps first (needs Edge + Pillow)

Rule of the design: the atmosphere (sky, clouds, wires, field) lives only in the hero.
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

THEMES = {
    "light": dict(sky="#CFE6EC", mist="#EEF5F2", field="#8DB596", aqua="#8CCFD6", text="#2F4A3E",
                  muted="#5E7A70", rule="#C9D9D3", surface="#F6FAF8", cloud=0.6, wire=0.3),
    "dark": dict(sky="#16302F", mist="#0F1E1F", field="#5E8F72", aqua="#4FA3AC", text="#E3F0EC",
                 muted="#9DB5AE", rule="#2C4644", surface="#132625", cloud=0.09, wire=0.3),
}
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def svg(w, h, body, label, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" font-family="{FONT}">'
            f"<title>{escape(label)}</title><style>{css}{REDUCED}</style>{body}</svg>")


def lines(x, y, rows, size, fill, lh):
    return "".join(f'<text x="{x}" y="{y + i * lh:.0f}" font-size="{size}" fill="{fill}">{escape(r)}</text>'
                   for i, r in enumerate(rows))


# ---------- hero: the one atmospheric moment ----------
def hero(t):
    """Overcast sky, drifting cloud banks, power lines over a rice field (Lily Chou-Chou)."""
    h = 230
    clouds = "".join(
        f'<ellipse class="c" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#FFFFFF" fill-opacity="{a * t["cloud"]:.2f}" '
        f'filter="url(#soft)" style="animation-duration:{d}s"/>'
        for x, y, rx, ry, a, d in [(640, 46, 180, 30, 1, 70), (380, 22, 150, 20, .7, 90), (790, 112, 120, 18, .6, 80)])

    def pole(x, top, arm, sw):  # a pole and its cross-arm, kept right of the name
        return (f'<line x1="{x}" y1="{top}" x2="{x}" y2="196" stroke-width="{sw}"/>'
                f'<line x1="{x - arm}" y1="{top + 10}" x2="{x + arm}" y2="{top + 10}" stroke-width="{sw}"/>')

    def sag(x1, y1, x2, y2, d):
        return f'M{x1} {y1} Q {(x1 + x2) / 2} {max(y1, y2) + d} {x2} {y2}'

    near, far = (640, 34, 22), (800, 120, 11)   # x, top, arm half-width
    wires = []
    for k in (-1, 0, 1):
        nx, ny = near[0] + k * near[2], near[1] + 10
        fx, fy = far[0] + k * far[2], far[1] + 10
        wires += [sag(nx, ny, fx, fy, 16),                    # near pole -> far pole
                  sag(fx, fy, 880, fy + 8 + k * 2, 4),        # far pole -> off the right edge
                  sag(nx, ny, 520 + k * 14, -8, 12)]          # near pole -> up out of frame, above the name
    wire_svg = "".join(f'<path d="{d}"/>' for d in wires)
    body = f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['sky']}"/><stop offset="1" stop-color="{t['mist']}"/></linearGradient>
<filter id="soft" x="-50%" y="-80%" width="200%" height="260%"><feGaussianBlur stdDeviation="14"/></filter>
<clipPath id="clip"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{h}" fill="url(#sky)"/>
  {clouds}
  <g class="lines" fill="none" stroke="{t['text']}" stroke-opacity="{t['wire']}">
    <g stroke-width="1">{wire_svg}</g>{pole(*near, 1.6)}{pole(*far, 1)}
  </g>
  <path class="f1" d="M-40 188 C 120 168, 260 198, 420 180 S 700 163, 880 184 V 240 H -40 Z" fill="{t['field']}" fill-opacity=".32"/>
  <path class="f2" d="M-40 207 C 150 191, 330 217, 520 199 S 760 195, 880 209 V 240 H -40 Z" fill="{t['field']}" fill-opacity=".48"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="15.5" fill="none" stroke="{t['rule']}"/>
<text x="40" y="88" font-size="44" font-weight="300" letter-spacing=".5" fill="{t['text']}">Jamir Oasis Andrade</text>
<text x="42" y="120" font-size="17" fill="{t['text']}">Full-stack web developer · digitizing traditional workflows</text>
<text x="42" y="146" font-size="13.5" fill="{t['muted']}">Freelance  ·  Veris backend  ·  GCI World cohort  ·  DOST scholar  ·  CS at VSU</text>"""
    css = """
.c{animation:cloud linear infinite alternate}
@keyframes cloud{to{transform:translateX(-60px)}}
.lines{animation:sway 9s ease-in-out infinite alternate}
@keyframes sway{to{transform:translateY(1.5px)}}
.f1{animation:drift 30s ease-in-out infinite alternate}
.f2{animation:drift 22s ease-in-out infinite alternate-reverse}
@keyframes drift{from{transform:translateX(-12px)}to{transform:translateX(12px)}}"""
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
    "florence": dict(slug="florence", status="LIVE  ·  INVITE ONLY", title="Project Florence",
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
            "card-florence": pair_card(t, PROJECTS["florence"], photo("florence", 0, 0, 412, 250), "left"),
            "card-ncs": pair_card(t, PROJECTS["ncs"], photo("ncs", 0, 0, 412, 250), "right"),
        }
        for name, s in files.items():
            (OUT / f"{name}-{mode}.svg").write_text(s, encoding="utf-8")
    import xml.dom.minidom as md  # self-check: every file is well-formed XML
    for f in OUT.glob("*.svg"):
        md.parse(str(f))
    print(f"ok: {len(list(OUT.glob('*.svg')))} svgs,", sum(f.stat().st_size for f in OUT.glob('*.svg')) // 1024, "KB total")
