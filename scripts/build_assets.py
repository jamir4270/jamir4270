"""Generate the profile README SVGs (light + dark) from one palette.

Run: python scripts/build_assets.py   -> writes assets/*.svg
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 840
PAD = 16  # one inset for every panel so edges line up and shadows are not clipped
# shortcut: system font stack instead of outlined text (Segoe UI is the aero-era face but can't be redistributed as paths)
FONT = "'Segoe UI', 'Frutiger', 'Helvetica Neue', 'Noto Sans', Arial, sans-serif"

THEMES = {
    "light": dict(
        sky="#CFE6EC", mist="#EEF5F2", field="#8DB596", aqua="#8CCFD6", ether="#C9C3DE",
        text="#2F4A3E", muted="#5E7A70", line="#FFFFFF", glass="#FFFFFF", glass_a=0.55,
        chip="#FFFFFF", chip_a=0.7, chip_text="#2F4A3E", shadow="#2F4A3E", shadow_a=0.12, gloss=0.45,
    ),
    "dark": dict(
        sky="#16302F", mist="#0F1E1F", field="#5E8F72", aqua="#4FA3AC", ether="#8F86B3",
        text="#E3F0EC", muted="#9DB5AE", line="#BFE3E6", glass="#BFE3E6", glass_a=0.08,
        chip="#BFE3E6", chip_a=0.12, chip_text="#DCEDE8", shadow="#000000", shadow_a=0.45, gloss=0.10,
    ),
}

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def text_w(s, size):
    return len(s) * size * 0.56  # rough average glyph width, good enough for chip sizing


def chips(items, x, y, t, size=12):
    out = []
    for it in items:
        w = text_w(it, size) + 20
        out.append(
            f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{t["chip"]}" '
            f'fill-opacity="{t["chip_a"]}" stroke="{t["line"]}" stroke-opacity=".6"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 16}" text-anchor="middle" font-size="{size}" '
            f'fill="{t["chip_text"]}">{escape(it)}</text>'
        )
        x += w + 8
    return "".join(out)


def defs(t, uid):
    return f"""<defs>
<linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{t['sky']}"/><stop offset="1" stop-color="{t['mist']}"/></linearGradient>
<linearGradient id="gloss{uid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity="{t['gloss']}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<linearGradient id="sweep{uid}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/><stop offset=".5" stop-color="#FFFFFF" stop-opacity=".35"/>
  <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<radialGradient id="orb{uid}" cx=".35" cy=".3" r=".75">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".35" stop-color="{t['aqua']}" stop-opacity=".55"/>
  <stop offset="1" stop-color="{t['field']}" stop-opacity=".35"/></radialGradient>
<radialGradient id="haze{uid}" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{t['ether']}" stop-opacity=".55"/><stop offset="1" stop-color="{t['ether']}" stop-opacity="0"/></radialGradient>
<filter id="shadow{uid}" x="-5%" y="-10%" width="110%" height="130%">
  <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="{t['shadow']}" flood-opacity="{t['shadow_a']}"/></filter>
</defs>"""


def svg(h, body, label, css):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" '
        f'role="img" aria-label="{escape(label)}" font-family="{FONT}">'
        f"<title>{escape(label)}</title><style>{css}{REDUCED}</style>{body}</svg>"
    )


def bubble(cx, cy, r, dur, delay, uid):
    return (
        f'<circle class="b" cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb{uid})" stroke="#FFFFFF" '
        f'stroke-opacity=".7" style="animation-duration:{dur}s;animation-delay:-{delay}s"/>'
    )


def hero(t, uid="h"):
    h = 250
    bubbles = "".join(
        bubble(cx, cy, r, d, dl, uid)
        for cx, cy, r, d, dl in [
            (90, 210, 14, 26, 3), (180, 240, 7, 20, 11), (560, 230, 18, 32, 8), (640, 250, 9, 22, 15),
            (720, 220, 12, 28, 1), (780, 245, 6, 18, 6), (470, 255, 8, 24, 19), (300, 250, 5, 19, 9),
        ]
    )
    body = f"""{defs(t, uid)}
<clipPath id="clip{uid}"><rect x="{PAD}" y="0" width="{W - 2 * PAD}" height="{h}" rx="20"/></clipPath>
<g clip-path="url(#clip{uid})">
  <rect width="{W}" height="{h}" fill="url(#sky{uid})"/>
  <ellipse class="haze" cx="680" cy="40" rx="260" ry="140" fill="url(#haze{uid})"/>
  <path class="f1" d="M-40 205 C 120 180, 260 215, 420 195 S 700 175, 880 200 V 260 H -40 Z" fill="{t['field']}" fill-opacity=".35"/>
  <path class="f2" d="M-40 225 C 150 205, 330 235, 520 215 S 760 210, 880 225 V 260 H -40 Z" fill="{t['field']}" fill-opacity=".5"/>
  {bubbles}
  <rect width="{W}" height="{h * 0.48:.0f}" fill="url(#gloss{uid})"/>
  <rect class="sweep" x="-260" y="0" width="200" height="{h}" fill="url(#sweep{uid})" transform="skewX(-18)"/>
</g>
<rect x="{PAD + .5}" y=".5" width="{W - 2 * PAD - 1}" height="{h - 1}" rx="19.5" fill="none" stroke="{t['line']}" stroke-opacity=".7"/>
<text x="48" y="96" font-size="44" font-weight="300" letter-spacing=".5" fill="{t['text']}">Jamir Oasis Andrade</text>
<text x="50" y="128" font-size="17" fill="{t['muted']}">Full-stack web developer · digitizing traditional workflows</text>
{chips(['Freelance', 'Veris · Backend', 'GCI World Cohort', 'DOST Scholar', 'CS @ VSU'], 50, 148, t)}"""
    css = """
.b{animation:rise linear infinite}
@keyframes rise{0%{transform:translate(0,0);opacity:0}12%{opacity:.9}50%{transform:translate(8px,-110px)}
88%{opacity:.8}100%{transform:translate(-6px,-230px);opacity:0}}
.sweep{animation:sweep 16s ease-in-out infinite}
@keyframes sweep{0%,55%{transform:skewX(-18deg) translateX(0)}85%,100%{transform:skewX(-18deg) translateX(1400px)}}
.haze{animation:breathe 14s ease-in-out infinite alternate}
@keyframes breathe{from{opacity:.6}to{opacity:1}}
.f1{animation:drift 30s ease-in-out infinite alternate}
.f2{animation:drift 22s ease-in-out infinite alternate-reverse}
@keyframes drift{from{transform:translateX(-14px)}to{transform:translateX(14px)}}"""
    return svg(h, body, "Jamir Oasis Andrade, full-stack web developer", css)


def card(t, title, lines, stack, initial, delay, uid):
    h, pad = 172 + 2 * (PAD - 8), PAD
    cw, ch = W - 2 * pad, h - 2 * pad
    desc = "".join(
        f'<text x="128" y="{80 + i * 21}" font-size="14.5" fill="{t["muted"]}">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    body = f"""{defs(t, uid)}
<g filter="url(#shadow{uid})">
  <rect x="{pad}" y="{pad}" width="{cw}" height="{ch}" rx="16" fill="url(#sky{uid})"/>
  <rect x="{pad}" y="{pad}" width="{cw}" height="{ch}" rx="16" fill="{t['glass']}" fill-opacity="{t['glass_a']}"/>
</g>
<clipPath id="clip{uid}"><rect x="{pad}" y="{pad}" width="{cw}" height="{ch}" rx="16"/></clipPath>
<g clip-path="url(#clip{uid})">
  <rect x="{pad}" y="{pad}" width="{cw}" height="{ch * 0.45:.0f}" fill="url(#gloss{uid})"/>
  <rect class="sweep" x="-220" y="0" width="160" height="{h}" fill="url(#sweep{uid})" transform="skewX(-18)"
        style="animation-delay:{delay}s"/>
</g>
<rect x="{pad + .5}" y="{pad + .5}" width="{cw - 1}" height="{ch - 1}" rx="15.5" fill="none" stroke="{t['line']}" stroke-opacity=".75"/>
<g class="orb" style="animation-delay:-{delay}s">
  <circle cx="72" cy="{h / 2:.0f}" r="34" fill="url(#orb{uid})" stroke="#FFFFFF" stroke-opacity=".8"/>
  <ellipse cx="62" cy="{h / 2 - 16:.0f}" rx="16" ry="8" fill="#FFFFFF" fill-opacity=".6"/>
  <text x="72" y="{h / 2 + 9:.0f}" text-anchor="middle" font-size="26" font-weight="300" fill="{t['text']}">{initial}</text>
</g>
<text x="128" y="52" font-size="22" font-weight="600" fill="{t['text']}">{escape(title)}</text>
<text x="{W - 40}" y="52" text-anchor="end" font-size="18" fill="{t['muted']}">↗</text>
{desc}
{chips(stack, 128, 124, t)}"""
    css = """
.sweep{animation:sweep 18s ease-in-out infinite}
@keyframes sweep{0%,60%{transform:skewX(-18deg) translateX(0)}90%,100%{transform:skewX(-18deg) translateX(1300px)}}
.orb{animation:bob 7s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(-3px)}to{transform:translateY(3px)}}"""
    return svg(h, body, f"{title}: {' '.join(lines)}", css)


def stack(t, uid="s"):
    rows = [
        ("Web", ["Next.js", "React", "TypeScript", "Tailwind CSS", "Supabase", "PostgreSQL", "Vercel"]),
        ("Backend", ["C#", ".NET / ASP.NET MVC", "Node.js", "Firebase"]),
        ("Mobile", ["Flutter", "Dart"]),
        ("Data & AI", ["Python", "RAG pipelines", "Local LLMs", "Agentic SWE", "C / C++"]),
    ]
    h, pad = 40 + len(rows) * 40 + 2 * PAD - 8, PAD
    body = [f"""{defs(t, uid)}
<g filter="url(#shadow{uid})">
  <rect x="{pad}" y="{pad}" width="{W - 2 * pad}" height="{h - 2 * pad}" rx="16" fill="url(#sky{uid})"/>
  <rect x="{pad}" y="{pad}" width="{W - 2 * pad}" height="{h - 2 * pad}" rx="16" fill="{t['glass']}" fill-opacity="{t['glass_a']}"/>
</g>
<rect x="{pad}" y="{pad}" width="{W - 2 * pad}" height="{(h - 2 * pad) * 0.35:.0f}" rx="16" fill="url(#gloss{uid})"/>
<rect x="{pad + .5}" y="{pad + .5}" width="{W - 2 * pad - 1}" height="{h - 2 * pad - 1}" rx="15.5" fill="none" stroke="{t['line']}" stroke-opacity=".75"/>"""]
    for i, (label, items) in enumerate(rows):
        y = 32 + i * 40
        body.append(
            f'<text x="40" y="{y + 16}" font-size="13" font-weight="600" letter-spacing="1" '
            f'fill="{t["muted"]}">{escape(label.upper())}</text>{chips(items, 150, y, t)}'
        )
    alt = "; ".join(f"{l}: {', '.join(i)}" for l, i in rows)
    return svg(h, "".join(body), f"Tech stack. {alt}", "")


def wave(t, uid="w"):
    h = 70
    p = "M0 40 C 105 20, 210 60, 315 40 S 525 20, 630 40 S 840 60, 945 40 S 1155 20, 1260 40 S 1470 60, 1575 40 S 1785 20, 1890 40 V 70 H 0 Z"
    body = f"""{defs(t, uid)}
<path class="w1" d="{p}" fill="{t['aqua']}" fill-opacity=".25"/>
<path class="w2" d="{p}" fill="{t['field']}" fill-opacity=".3" transform="translate(0 10)"/>"""
    css = """
.w1{animation:flow 28s linear infinite}.w2{animation:flow 40s linear infinite reverse}
@keyframes flow{from{transform:translateX(0)}to{transform:translateX(-630px)}}"""
    return svg(h, body, "decorative wave", css)


PROJECTS = [
    ("oreo", "Oreo Finance", ["Personal finance tracker for income, expenses, transfers and budgets,",
                              "across multiple accounts and currencies."],
     ["Next.js 16", "React 19", "Supabase", "Tailwind CSS"], "O"),
    ("florence", "Project Florence", ["Faculty of Nursing records platform: council events and payments,",
                                      "merits, demerits, service hours and clearance."],
     ["Next.js 16", "PostgreSQL", "Supabase Auth", "Cloudflare R2"], "F"),
    ("ncs", "VSU Nursing Conduct System", ["Replaces a paper logbook with role-based merit and demerit tracking",
                                           "for students, faculty and admins, with email alerts."],
     ["Next.js 16", "Supabase", "shadcn/ui", "Nodemailer"], "N"),
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for mode, t in THEMES.items():
        (OUT / f"hero-{mode}.svg").write_text(hero(t), encoding="utf-8")
        (OUT / f"stack-{mode}.svg").write_text(stack(t), encoding="utf-8")
        (OUT / f"wave-{mode}.svg").write_text(wave(t), encoding="utf-8")
        for i, (slug, title, lines, st, ini) in enumerate(PROJECTS):
            (OUT / f"card-{slug}-{mode}.svg").write_text(card(t, title, lines, st, ini, i * 4, slug), encoding="utf-8")
    import xml.dom.minidom as md  # self-check: every file is well-formed XML
    for f in OUT.glob("*.svg"):
        md.parse(str(f))
    print(f"ok: {len(list(OUT.glob('*.svg')))} svgs")
