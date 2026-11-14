import json, base64, sys
from playwright.sync_api import sync_playwright
S = '/tmp/claude-0/-home-claude/9af8fd2f-ee91-5254-9760-53eb87908abc/scratchpad/upd'
def b64(f, mime): return f"data:{mime};base64," + base64.b64encode(open(f, 'rb').read()).decode()
FONT = b64(f'{S}/Rubik.ttf', 'font/ttf'); PH1 = b64(f'{S}/ph_analysis.png', 'image/png'); PH2 = b64(f'{S}/ph_replay.png', 'image/png')
T = {
 'en': dict(dir='ltr', head="The new<br>version is out", sub="New design, and the analysis now<br>runs on <span class=c>GAL</span>, our own model", cta="Update the app", as_='as_en', gp='gp_en'),
 'he': dict(dir='rtl', head="הגרסה החדשה<br>באוויר", sub="עיצוב חדש, והניתוח עכשיו<br>רץ על <span class=c>GAL</span>, המודל שלנו", cta="עדכנו את האפליקציה", as_='as_he', gp='gp_he'),
}
def html(L):
    t = T[L]; al = 'left' if t['dir'] == 'ltr' else 'right'
    return f"""<!doctype html><html lang={L} dir={t['dir']}><head><meta charset=utf-8><style>
@font-face{{font-family:R;src:url({FONT});font-weight:300 900}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#2D242A;font-family:R,sans-serif;color:#F5F1F7;position:relative;overflow:hidden}}
.wm{{position:absolute;top:262px;left:80px;font-weight:800;font-size:44px;letter-spacing:-0.5px;direction:ltr}}
.wm b{{color:#00CDFE;font-weight:800}}
.rule{{position:absolute;left:80px;width:920px;height:2px;background:rgba(245,241,247,.18)}}
h1{{position:absolute;top:352px;left:80px;width:920px;font-weight:800;font-size:104px;line-height:1.02;letter-spacing:-2px;text-align:{al}}}
.sub{{position:absolute;top:600px;left:80px;width:920px;font-weight:500;font-size:48px;line-height:1.28;color:rgba(245,241,247,.86);text-align:{al}}}
.c{{color:#00CDFE;font-weight:700}}
.ph{{position:absolute;top:1000px;width:455px;height:980px;border-radius:52px;overflow:hidden;border:3px solid rgba(245,241,247,.22);background:#1b1420}}
.ph img{{width:100%;display:block}}
.cta{{position:absolute;top:772px;left:80px;width:920px;font-weight:700;font-size:46px;text-align:{al};color:#F5F1F7}}
.bd{{position:absolute;top:848px;left:80px;width:920px;display:flex;gap:28px;align-items:center;justify-content:{'flex-start' if t['dir']=='ltr' else 'flex-end'};direction:ltr}}
.bd img{{height:104px;display:block}}
</style></head><body>
<div class=wm>Surf<b>Tribe</b></div>
<div class=rule style="top:330px"></div>
<h1 id=h>{t['head']}</h1>
<div class=sub id=s>{t['sub']}</div>
<div class=ph id=p1 style="left:80px"><img src="{PH1}"></div>
<div class=ph id=p2 style="left:565px"><img src="{PH2}"></div>
<div class=cta id=c>{t['cta']}</div>
<div class=bd id=b><img id=b1 src="{b64(f"{S}/{t['as_']}.png",'image/png')}"><img id=b2 src="{b64(f"{S}/{t['gp']}.png",'image/png')}"></div>
</body></html>"""
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
    for L in ('en', 'he'):
        pg.set_content(html(L)); pg.wait_for_timeout(300)
        m = pg.evaluate("""() => Object.fromEntries(['h','s','p1','p2','c','b','b1','b2'].map(i=>{const r=document.getElementById(i).getBoundingClientRect();return [i,[Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)]]}))""")
        fonts = pg.evaluate("() => document.fonts.check('800 40px R')")
        pg.screenshot(path=f'{S}/story_update_{L}.png'); print(L, 'font R loaded:', fonts, json.dumps(m))
    br.close()
