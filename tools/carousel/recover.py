# Re-cover p09-p14 (22-27.10) with "callout + myth" hooks, and replace ווקס with שעווה on HE slides.
import base64, json, sys, os
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
R = '/home/claude/media-push/'
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
RUBIK = b64(R + 'appkit/Rubik.ttf'); MONO = b64(R + 'tools/carousel/JetBrainsMono.ttf')
CY = '#00CDFC'; BG = '46,37,42'; FG = '#F4F2F6'
HEAD = (f"<meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{RUBIK});font-weight:300 900}}"
        f"@font-face{{font-family:M;src:url(data:font/ttf;base64,{MONO});font-weight:100 800}}"
        "html,body{margin:0;background:transparent}*{box-sizing:border-box}</style>")
COVERS = json.load(open(R + 'tools/carousel/covers.json'))

def cover_html(img, lang, call, title):
    rtl = lang == 'HE'
    side = 'right:80px' if rtl else 'left:80px'
    callcss = ("font-family:R;font-weight:600;font-size:34px" if rtl else
               "font-family:M;font-weight:700;font-size:28px;letter-spacing:3px;text-transform:uppercase")
    return (HEAD + f"<body style='width:1080px;height:1350px;position:relative;overflow:hidden'>"
            f"<img src='data:image/jpeg;base64,{b64(img)}' style='position:absolute;left:0;top:0;width:1080px;height:1350px'>"
            f"<div style='position:absolute;left:0;right:0;top:790px;height:172px;background:linear-gradient(rgba({BG},0),rgba({BG},1))'></div>"
            f"<div style='position:absolute;left:0;right:0;top:960px;height:322px;background:rgb({BG})'></div>"
            f"<div style='position:absolute;{side};bottom:96px;width:920px;direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'}'>"
            f"<div style='{callcss};color:{CY};line-height:1;margin-bottom:22px'>{call}</div>"
            f"<div style='font-family:R;font-weight:900;font-size:{84 if not rtl else 88}px;line-height:1.02;color:{FG};letter-spacing:{-1.5 if not rtl else 0}px'>{title}</div>"
            "</div></body>")

def word_png(pg, text, weight, color):
    pg.set_content(HEAD + f"<body><span id=t style='font-family:R;font-weight:{weight};font-size:200px;color:{color};direction:rtl;white-space:nowrap;display:inline-block;padding:20px'>{text}</span></body>")
    pg.wait_for_timeout(100)
    pg.locator('#t').screenshot(path='/tmp/word.png', omit_background=True)
    im = Image.open('/tmp/word.png').convert('RGBA'); a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > 20); return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def patch(pg, f, box, old, text, weight):
    im = Image.open(R + f).convert('RGB'); a = np.asarray(im).astype(int)
    x0, y0, x1, y1 = box; reg = a[y0:y1, x0:x1]
    bg = np.median(np.concatenate([reg[0], reg[-1], reg[:, 0], reg[:, -1]]), axis=0)
    m = np.abs(reg - bg).sum(2) > 80; ys, xs = np.where(m)
    tx0, ty0, tx1, ty1 = xs.min() + x0, ys.min() + y0, xs.max() + x0, ys.max() + y0
    ink = reg[m]; col = ink[np.argmax(np.abs(ink - bg).sum(1))]
    color = '#%02x%02x%02x' % tuple(int(c) for c in col)
    # ink height of a reference glyph set: scale new word so its ink height equals old ink height
    k = (ty1 - ty0 + 1) / word_png(pg, old, weight, color).height   # same font size as the old word
    w = word_png(pg, text, weight, color)
    nw = w.resize((round(w.width * k), round(w.height * k)), Image.LANCZOS)
    oldk = word_png(pg, old, weight, color); base_off = 0
    out = im.copy(); out.paste(Image.new('RGB', (tx1 - tx0 + 13, ty1 - ty0 + 13), tuple(int(c) for c in bg)), (tx0 - 6, ty0 - 6))
    out.paste(nw, (tx1 + 1 - nw.width, ty0), nw)
    out.save(R + f, quality=95); print('patched', f, (tx0, ty0, tx1, ty1), '->', nw.size, color)

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    for c in ([] if '--p12' in sys.argv else COVERS):
        for lang in ('EN', 'HE'):
            f = f"{R}p{c['p']:02d}/{lang}_1.jpg"; orig = f.replace('_1.jpg', '_1_orig.jpg')
            if not os.path.exists(orig): os.rename(f, orig)
            pg.set_content(cover_html(orig, lang, c[lang]['call'], c[lang]['title'])); pg.wait_for_timeout(300)
            pg.screenshot(path='/tmp/cov.png', clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1350})
            Image.open('/tmp/cov.png').convert('RGB').save(f, quality=95); print('cover', f)
    if '--p12' in sys.argv:
        patch(pg, 'p12/HE_7.jpg', (120, 840, 1010, 910), 'מחר: ווקס וליש, כמו שצריך. עקבו כדי לא לפספס', 'מחר: שעווה וליש, כמו שצריך. עקבו כדי לא לפספס', 400)
    if '--wax' in sys.argv:
        patch(pg, 'p13/HE_2.jpg', (930, 95, 1010, 135), 'ווקס', 'שעווה', 500)
        patch(pg, 'p13/HE_6.jpg', (640, 305, 1010, 395), 'ווקס וליש', 'שעווה וליש', 800)
        patch(pg, 'p13/HE_7.jpg', (220, 725, 1010, 825), 'שמרו לפני שמווקסים', 'שמרו לסשן הבא', 800)
        patch(pg, 'p09/HE_4.jpg', (760, 450, 1010, 560), 'ווקס', 'שעווה', 800)
    b.close()
