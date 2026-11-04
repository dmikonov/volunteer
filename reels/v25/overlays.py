"""Transparent PNG overlays for reel 25 'מי נופל ראשון?' rendered by Chromium (correct RTL, Rubik)."""
import sys, json; sys.path.insert(0, '/home/claude/work/series')
from base import RUB, CYAN, CORAL, FOAM, PLUM
from pathlib import Path
from playwright.sync_api import sync_playwright
OV = Path('/home/claude/work/series/reels/guess25/ov'); OV.mkdir(exist_ok=True)
FF = f"@font-face{{font-family:Rubik;src:url(data:font/ttf;base64,{RUB});font-weight:300 900}}"
SH = "text-shadow:0 3px 14px rgba(0,0,0,.55),0 1px 3px rgba(0,0,0,.7)"
def page(body, w=1080, h=400):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{FF}
html,body{{margin:0;background:transparent;width:{w}px;height:{h}px;overflow:hidden}}
*{{font-family:Rubik;color:{FOAM}}}</style></head><body>{body}</body></html>"""
ITEMS = {}
# hook title
ITEMS['hook'] = (page(f"<div id=t dir=rtl style='position:absolute;left:0;right:0;top:20px;text-align:center;font-weight:800;font-size:94px;line-height:1.05;{SH}'>נחשו מי מהם<br>נופל ראשון?</div>", 1080, 260), 1080, 260)
# wordmark
ITEMS['mark'] = (page(f"<div id=t style='position:absolute;left:0;right:0;top:10px;text-align:center;font-weight:800;font-size:46px;direction:ltr;{SH}'>Surf<span style='color:{CYAN}'>Tribe</span></div>", 1080, 80), 1080, 80)
# number badges
for n in (1, 2):
    for tag, col in (('', CYAN), ('x', CORAL)):
        ITEMS[f'badge{n}{tag}'] = (page(f"<div id=t style='position:absolute;left:8px;top:8px;width:96px;height:96px;border-radius:50%;box-sizing:border-box;border:7px solid {col};background:rgba(45,36,42,.82);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:60px;line-height:1'>{n}</div>", 112, 112), 112, 112)
# subtitles (fixed height and centre are applied at composite time: PNG is full width, text centred at x=540)
SUBS = json.load(open('/home/claude/work/series/reels/guess25/subs.json'))
for k, t in SUBS.items():
    ITEMS['sub_' + k] = (page(f"<div style='position:absolute;left:0;right:0;top:6px;text-align:center'><span id=t dir=rtl style='display:inline-block;padding:10px 30px 14px;border-radius:22px;background:rgba(45,36,42,.62);font-weight:800;font-size:66px;line-height:1.1'>{t}</span></div>", 1080, 110), 1080, 110)
# knee-angle chips
for a in range(80, 181):
    col = CORAL if a >= 160 else CYAN
    ITEMS[f'chip{a}'] = (page(f"<div id=t dir=rtl style='position:absolute;right:6px;top:6px;padding:10px 22px;border-radius:999px;background:rgba(45,36,42,.85);border:3px solid {col};font-weight:800;font-size:44px;line-height:1;white-space:nowrap'>ברכיים <span style='direction:ltr;unicode-bidi:isolate;color:{col}'>{a}°</span></div>", 360, 90), 360, 90)
# end card
ITEMS['end'] = (page(f"""<div dir=rtl style='position:absolute;left:0;right:0;top:0;text-align:center'>
<div id=t style='font-weight:800;font-size:104px;line-height:1.05;{SH}'>מה ניחשתם?</div>
<div style='font-weight:800;font-size:64px;margin-top:26px;color:{CYAN};{SH}'>כתבו בתגובות</div>
<div style='font-weight:800;font-size:58px;margin-top:70px;direction:ltr;{SH}'>Surf<span style='color:{CYAN}'>Tribe</span></div></div>""", 1080, 420), 1080, 420)
boxes = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for name, (html, w, h) in ITEMS.items():
        pg.set_viewport_size({'width': w, 'height': h}); pg.set_content(html); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(60)
        r = pg.evaluate("""() => { const out=[]; for (const el of document.querySelectorAll('body *')) { const t=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()); if(!t) continue; const r=el.getBoundingClientRect(); out.push([r.left,r.top,r.right,r.bottom]); } 
          const f=document.fonts.check('800 66px Rubik'); return {boxes:out, rubik:f}; }""")
        xs = [q for bb in r['boxes'] for q in bb]
        boxes[name] = {'l': min(bb[0] for bb in r['boxes']), 't': min(bb[1] for bb in r['boxes']), 'r': max(bb[2] for bb in r['boxes']), 'b': max(bb[3] for bb in r['boxes']), 'rubik': r['rubik']}
        pg.screenshot(path=str(OV / f'{name}.png'), omit_background=True)
    b.close()
json.dump(boxes, open(OV / 'boxes.json', 'w'), indent=0)
print({k: v for k, v in boxes.items() if not k.startswith('chip')})
