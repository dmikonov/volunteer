"""Overlays v22 (1080x1920 transparent). Table = carousel p02 (published 15 Oct), so reel and post agree.
Rules: Rubik 800 headlines, text >= 44 px, no full stops, key text inside x 70-850 and y 230-1300
(subtitle band starts at y 1366), SurfTribe on screen in the first beat and at the end."""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

D = Path(__file__).resolve().parent
OUT = D / 'v22'; OUT.mkdir(exist_ok=True)
b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
FONT = 'data:font/ttf;base64,' + b64('/home/claude/media-push/forecast/Rubik.ttf')
CYAN, CORAL, AMBER = '#00CDFE', '#FF5150', '#F5A623'
CSS = (f"@font-face{{font-family:R;src:url({FONT})}}*{{margin:0;padding:0;box-sizing:border-box}}"
       "html,body{width:1080px;height:1920px;background:transparent;font-family:R;color:#fff}"
       ".sh{text-shadow:0 6px 28px rgba(0,0,0,.6),0 2px 6px rgba(0,0,0,.65)}"
       ".h{font-weight:800;letter-spacing:-1px;line-height:1.02}")
GRAD = "<div style='position:absolute;left:0;right:0;top:0;height:1050px;background:linear-gradient(rgba(0,0,0,.6),rgba(0,0,0,.3) 55%,rgba(0,0,0,0))'></div>"
WORD = f"<span style='font-weight:800'>Surf<span style='color:{CYAN}'>Tribe</span></span>"

# same rows as carousel p02 (ROWS_EN in work/series/p02/make.py)
ROWS = [('75°F+', '24°C+', 'Boardshorts or rash guard', CORAL),
        ('65-75°F', '18-24°C', '2 mm spring suit or top', AMBER),
        ('60-65°F', '16-18°C', '3/2 full suit', '#7FD8F0'),
        ('55-60°F', '13-16°C', '4/3 full suit', CYAN),
        ('48-55°F', '9-13°C', '4/3 or 5/4, add booties', '#4FA8FF'),
        ('Under 48°F', 'Under 9°C', '5/4 or 6/5, hooded', '#8FA2FF')]


def page(body, grad=True):
    return f"<html><head><style>{CSS}</style></head><body>{GRAD if grad else ''}{body}</body></html>"


def block(inner, top=260):
    return f"<div class=sh style='position:absolute;left:70px;width:780px;top:{top}px'>{inner}</div>"


def scale(level):
    dots = ''.join(f"<div style='width:{84 if i == level else 34}px;height:16px;border-radius:8px;background:{c if i == level else 'rgba(255,255,255,.35)'}'></div>"
                   for i, (_, _, _, c) in enumerate(ROWS))
    return (f"<div style='display:flex;gap:10px;align-items:center;margin-top:24px'><span style='font-size:44px;font-weight:700'>Warm</span>"
            f"{dots}<span style='font-size:44px;font-weight:700'>Cold</span></div>")


def row_card(i):
    f, c, s, col = ROWS[i]
    return page(block(f"<div class=h style='font-size:{136 if len(f) < 9 else 116}px;color:{col}'>{f}</div>"
                      f"<div style='font-weight:600;font-size:46px;margin:8px 0 18px'>{c} water</div>"
                      f"<div style='display:inline-block;max-width:780px;background:rgba(20,16,20,.66);border:2px solid rgba(255,255,255,.25);border-radius:22px;"
                      f"padding:12px 26px;font-weight:800;font-size:56px;line-height:1.1;text-wrap:balance;text-shadow:none'>{s}</div>{scale(i)}"))


def recap():
    rows = ''.join(
        f"<div style='padding:10px 22px;margin-bottom:10px;border-radius:18px;background:rgba(28,22,26,.86);border:2px solid rgba(255,255,255,.16)'>"
        f"<div style='font-weight:800;font-size:48px;color:{col}'>{f} <span style='font-weight:600;font-size:44px;color:#fff;opacity:.8'>{c}</span></div>"
        f"<div style='font-weight:700;font-size:44px;margin-top:2px'>{s}</div></div>" for f, c, s, col in ROWS)
    return page(f"<div style='position:absolute;left:70px;width:770px;top:240px'>"
                f"<div class='sh h' style='font-size:92px'>Save this</div>"
                f"<div class=sh style='font-size:46px;margin:4px 0 16px'>{WORD} <span style='font-weight:600'>· your AI surf coach</span></div>{rows}</div>", grad=False)


OVER = {
    # hook: the on-screen text is exactly the spoken line, so no second text competes with it (no subtitle in beat 0)
    'h0': page(block(f"<div style='font-size:52px;margin-bottom:10px'>{WORD}</div>"
                     f"<div class=h style='font-size:60px;margin-bottom:8px'>Nobody tells you this</div>"
                     f"<div class=h style='font-size:104px'>Water temp<br>picks your<br><span style='color:{CYAN}'>wetsuit</span></div>")),
    **{f'r{i}': row_card(i) for i in range(6)},
    'end': recap(),
}

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        for k, html in OVER.items():
            pg.set_content(html); pg.wait_for_timeout(200); pg.evaluate('document.fonts.ready')
            bad = pg.evaluate("""() => { const out = [];
              for (const el of document.querySelectorAll('body *')) {
                const t = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
                if (!t) continue;
                const r = el.getBoundingClientRect(), cs = getComputedStyle(el), fs = parseFloat(cs.fontSize), fw = +cs.fontWeight;
                const why = [];
                if (/[.]$/.test(t)) why.push('fullstop');
                if (/[\\u2013\\u2014]/.test(t)) why.push('dash');
                if (fs < 44) why.push('size ' + fs);
                if (fw >= 900) why.push('w900');
                if (r.left < 69 || r.right > 851) why.push('x ' + Math.round(r.left) + '-' + Math.round(r.right));
                if (r.top < 230 || r.bottom > 1300) why.push('y ' + Math.round(r.top) + '-' + Math.round(r.bottom));
                if (why.length) out.push(t + ': ' + why.join(','));
              } return out; }""")
            box = pg.evaluate("() => { let b = [1e9, 1e9, 0, 0]; for (const el of document.querySelectorAll('body *')) { const t = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()); if (!t) continue; const r = el.getBoundingClientRect(); b = [Math.min(b[0], r.left), Math.min(b[1], r.top), Math.max(b[2], r.right), Math.max(b[3], r.bottom)]; } return b.map(Math.round); }")
            print(k, 'text bbox', box, 'VIOLATIONS', bad or 'none')
            pg.screenshot(path=str(OUT / f'{k}.png'), omit_background=True)
        b.close()
