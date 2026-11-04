"""Overlays v22 (1080x1920 transparent). Table = carousel p02 (ROWS_EN), so reel and post say the same thing.
Rules: Rubik 800 headlines, all text >= 44 px, no full stops, key text inside x 70-850 and y 230-1440,
SurfTribe visible in the first beat, the hook shows ONE text (the spoken line)."""
import base64, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parent
OUT = D / 'v22'; OUT.mkdir(exist_ok=True)
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
FONT = 'data:font/ttf;base64,' + b64('/home/claude/media-push/forecast/Rubik.ttf')
CYAN, CORAL, AMBER, ICE = '#00CDFE', '#FF5150', '#F5A623', '#7FD8F0'
CSS = (f"@font-face{{font-family:R;src:url({FONT})}}*{{margin:0;padding:0;box-sizing:border-box}}"
       "html,body{width:1080px;height:1920px;background:transparent;font-family:R;color:#fff}"
       ".sh{text-shadow:0 6px 28px rgba(0,0,0,.6),0 2px 6px rgba(0,0,0,.65)}"
       ".h{font-weight:800;letter-spacing:-1px;line-height:1.02}")
GRAD = "<div style='position:absolute;left:0;right:0;top:0;height:1050px;background:linear-gradient(rgba(0,0,0,.55),rgba(0,0,0,.25) 55%,rgba(0,0,0,0))'></div>"
WORD = f"<span style='font-weight:800'>Surf<span style='color:{CYAN}'>Tribe</span></span>"

# exactly the carousel p02 table (work/series/p02/make.py ROWS_EN)
ROWS = [('75°F+', '24°C+', 'Boardshorts or rash guard', CORAL), ('65-75°F', '18-24°C', '2 mm spring suit or top', AMBER),
        ('60-65°F', '16-18°C', '3/2 full suit', ICE), ('55-60°F', '13-16°C', '4/3 full suit', CYAN),
        ('48-55°F', '9-13°C', '4/3 or 5/4, add booties', CYAN), ('Under 48°F', 'Under 9°C', '5/4 or 6/5, hooded', CYAN)]


def page(body, grad=True):
    return f"<html><head><style>{CSS}</style></head><body>{GRAD if grad else ''}{body}</body></html>"


def block(inner, top=260):
    return f"<div class=sh style='position:absolute;left:70px;width:780px;top:{top}px'>{inner}</div>"


def scale(level):
    dots = ''.join(f"<div style='width:{84 if i == level else 34}px;height:16px;border-radius:8px;background:{c if i == level else 'rgba(255,255,255,.35)'}'></div>"
                   for i, (_, _, _, c) in enumerate(ROWS))
    return (f"<div style='display:flex;gap:9px;align-items:center;margin-top:26px'><span style='font-size:44px;font-weight:700'>Warm</span>"
            f"{dots}<span style='font-size:44px;font-weight:700'>Cold</span></div>")


def row_card(i):
    f, c, s, col = ROWS[i]
    return page(block(f"<div class=h style='font-size:{140 if len(f) < 9 else 120}px;color:{col}'>{f}</div>"
                      f"<div style='font-weight:600;font-size:46px;margin:8px 0 20px'>{c} water</div>"
                      f"<div style='display:inline-block;background:rgba(20,16,20,.66);border:2px solid rgba(255,255,255,.25);border-radius:22px;"
                      f"padding:12px 26px;font-weight:800;font-size:{58 if len(s) < 20 else 52}px;white-space:nowrap;text-shadow:none'>{s}</div>{scale(i)}"))


def recap():
    rows = ''.join(
        f"<div style='padding:10px 22px;margin-bottom:10px;border-radius:20px;background:rgba(28,22,26,.86);border:2px solid rgba(255,255,255,.16)'>"
        f"<div style='font-weight:800;font-size:48px;color:{col}'>{f} <span style='font-weight:600;font-size:44px;color:#fff;opacity:.8'>{c}</span></div>"
        f"<div style='font-weight:700;font-size:44px;margin-top:2px'>{s}</div></div>" for f, c, s, col in ROWS)
    return page(f"<div style='position:absolute;left:70px;width:770px;top:240px'>"
                f"<div class='sh h' style='font-size:92px'>Save this</div>"
                f"<div class=sh style='font-weight:700;font-size:44px;margin:6px 0 18px'>{WORD} <span style='font-weight:600'>· your AI surf coach</span></div>{rows}</div>", grad=False)


OVER = {
    'h0': page(block(f"<div style='font-size:52px;margin-bottom:14px'>{WORD}</div>"
                     f"<div style='font-size:60px;font-weight:700;margin-bottom:10px'>Nobody tells you this:</div>"
                     f"<div class=h style='font-size:104px'>Pick your<br>wetsuit by<br><span style='color:{CYAN}'>water temp</span></div>")),
    **{f'r{i}': row_card(i) for i in range(6)},
    'end': recap(),
}

CHECK = """() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const t = w.currentNode.textContent.trim(); if (!t) continue;
    const r = document.createRange(); r.selectNodeContents(w.currentNode); const b = r.getBoundingClientRect();
    const cs = getComputedStyle(w.currentNode.parentElement);
    out.push({t, x0: b.left, x1: b.right, y0: b.top, y1: b.bottom, fs: parseFloat(cs.fontSize), fw: cs.fontWeight}); } return out; }"""

if __name__ == '__main__':
    bad = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for k, html in OVER.items():
            pg.set_content(html); pg.wait_for_timeout(150); pg.evaluate('document.fonts.ready')
            for n in pg.evaluate(CHECK):
                t = n['t']
                if re.search(r'\.$', t) or re.search('[–—]', t): bad.append((k, 'punct', t))
                if n['fs'] < 44: bad.append((k, 'small', t, n['fs']))
                if n['fw'] == '900': bad.append((k, 'w900', t))
                if n['x0'] < 70 - 1 or n['x1'] > 850 or n['y0'] < 230 or n['y1'] > 1440: bad.append((k, 'zone', t, round(n['x0']), round(n['x1']), round(n['y0']), round(n['y1'])))
            pg.screenshot(path=str(OUT / f'{k}.png'), omit_background=True)
        b.close()
    print('TEXT_CHECK', 'PASS' if not bad else bad)
