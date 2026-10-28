# 28.10 carousel "board in the foam" (HE + EN), real Pexels stills, style of p09-p14 (plum panel, cyan accents, Rubik + JetBrains Mono)
# usage: python3 make_c28.py <stills_dir> <out_dir>
import base64, json, sys, os
from playwright.sync_api import sync_playwright
R = os.path.dirname(os.path.abspath(__file__)) + '/../../'
ST, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
RUBIK = b64(R + 'appkit/Rubik.ttf'); MONO = b64(R + 'tools/carousel/JetBrainsMono.ttf')
CY = '#00CDFC'; BG = 'rgb(46,37,42)'; FG = '#F4F2F6'; CO = '#FF5150'
HEAD = (f"<meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{RUBIK});font-weight:300 900}}"
        f"@font-face{{font-family:M;src:url(data:font/ttf;base64,{MONO});font-weight:100 800}}"
        f"html,body{{margin:0}}*{{box-sizing:border-box}}body{{width:1080px;height:1350px;position:relative;overflow:hidden;background:{BG}}}</style>")
C = json.load(open(os.path.dirname(os.path.abspath(__file__)) + '/c28.json'))

def img(f, x, y, w, h, pos='50% 50%', r=0):
    return f"<img src='data:image/jpeg;base64,{b64(ST + '/' + f)}' style='position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;object-fit:cover;object-position:{pos};border-radius:{r}px'>"

def mark(rtl):
    side = 'right:56px' if rtl else 'left:56px'
    return f"<div style='position:absolute;top:52px;{side};font:800 40px R;color:#fff;text-shadow:0 2px 8px rgba(0,0,0,.45)'>Surf<span style='color:{CY}'>Tribe</span></div>"

def foot(rtl, n, N, handle):
    side = 'left:56px' if rtl else 'right:56px'
    t = f"{n}/{N} · {handle}" if rtl else f"{handle} · {n}/{N}"
    return f"<div style='position:absolute;bottom:40px;{side};font:500 26px R;color:rgba(244,242,246,.75);direction:ltr'>{t}</div>"

def label_css(rtl, size=30):
    return (f"font:600 {size + 4}px R" if rtl else f"font:700 {size}px M;letter-spacing:3px;text-transform:uppercase")

def cover(s, L, rtl, n, N):
    side = 'right:72px' if rtl else 'left:72px'
    return (HEAD + "<body>" + img(s['img'], 0, 0, 1080, 1000, s.get('pos', '50% 50%')) +
            f"<div style='position:absolute;left:0;right:0;top:760px;height:240px;background:linear-gradient(rgba(46,37,42,0),{BG})'></div>" + mark(rtl) +
            f"<div style='position:absolute;{side};bottom:110px;width:936px;direction:{'rtl' if rtl else 'ltr'};text-align:{'right' if rtl else 'left'}'>"
            f"<div style='{label_css(rtl)};color:{CY};line-height:1;margin-bottom:24px'>{L['call']}</div>"
            f"<div style='font:900 {96 if rtl else 92}px/1.02 R;color:{FG};letter-spacing:{0 if rtl else -1.5}px'>{L['title']}</div></div>"
            + foot(rtl, n, N, C['handle'][L['lang']]) + "</body>")

def step(s, L, rtl, n, N):
    PW = 430  # text panel width
    px = 1080 - PW if rtl else 0; ix = 0 if rtl else PW
    al = 'right' if rtl else 'left'
    x_badge = ''
    if s.get('x'):
        x_badge = (f"<div style='position:absolute;top:70px;{'left' if rtl else 'right'}:60px;width:150px;height:150px;border-radius:50%;background:{CO};display:flex;align-items:center;justify-content:center;box-shadow:0 4px 18px rgba(0,0,0,.4)'>"
                   "<svg width='80' height='80' viewBox='0 0 80 80'><path d='M14 14 L66 66 M66 14 L14 66' stroke='#fff' stroke-width='14' stroke-linecap='round'/></svg></div>")
    return (HEAD + "<body>" + img(s['img'], ix, 0, 1080 - PW, 1350, s.get('pos', '50% 50%')) + x_badge +
            f"<div style='position:absolute;left:{px}px;top:0;width:{PW}px;height:1350px;background:{BG};padding:84px 52px;direction:{'rtl' if rtl else 'ltr'};text-align:{al}'>"
            f"<div style='{label_css(rtl, 28)};color:{CY};margin-bottom:34px'>{L['label']}</div>"
            f"<div style='font:900 210px/0.9 R;color:{CY};margin-bottom:40px'>{s['n']}</div>"
            f"<div style='font:800 {64 if rtl else 62}px/1.05 R;color:{FG};margin-bottom:34px'>{L['title']}</div>"
            f"<div style='font:400 46px/1.25 R;color:{FG}'>{L['body']}</div></div>"
            + foot(rtl, n, N, C['handle'][L['lang']]) + "</body>")

def final(s, L, rtl, n, N):
    al = 'right' if rtl else 'left'; d = 'rtl' if rtl else 'ltr'
    return (HEAD + "<body>" + mark(rtl) + img(s['img'], 60, 140, 960, 560, s.get('pos', '50% 50%'), 28) +
            f"<div style='position:absolute;left:72px;right:72px;top:770px;direction:{d};text-align:{al}'>"
            f"<div style='font:900 {80 if rtl else 76}px/1.04 R;color:{FG};margin-bottom:30px'>{L['title']}</div>"
            f"<div style='font:400 46px/1.3 R;color:{FG};margin-bottom:44px'>{L['body']}</div>"
            f"<div style='display:flex;align-items:center;gap:28px;flex-direction:{'row' if not rtl else 'row'}'>"
            f"<span style='background:{CY};color:#2D242A;border-radius:40px;padding:14px 30px;{label_css(rtl, 28)};direction:{d}'>{L['pill']}</span>"
            f"<span style='{label_css(rtl, 24)};color:rgba(244,242,246,.85)'>{L['app']}</span></div></div>"
            + foot(rtl, n, N, C['handle'][L['lang']]) + "</body>")

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    for lang in ('EN', 'HE'):
        rtl = lang == 'HE'; N = len(C['slides'])
        for i, s in enumerate(C['slides'], 1):
            L = dict(s[lang], lang=lang)
            html = {'cover': cover, 'step': step, 'final': final}[s['t']](s, L, rtl, i, N)
            pg.set_content(html); pg.wait_for_timeout(250)
            pg.screenshot(path=f'{OUT}/{lang}_{i}.jpg', type='jpeg', quality=92)
    b.close()
print('ok', OUT)
