import base64, sys, json
from playwright.sync_api import sync_playwright
F = base64.b64encode(open('/home/claude/media-push/appkit/Rubik.ttf','rb').read()).decode()
CY='#00CDFC'; PLATE='rgba(20,20,28,.70)'
def page(body, top):
    return (f"<!doctype html><html><head><meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{F});font-weight:300 900}}"
      "html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}*{font-family:R;box-sizing:border-box}"
      f".hook{{position:absolute;top:{top}px;left:80px;white-space:nowrap;font-weight:800;font-size:98px;line-height:1.05;color:#f4f2f7;-webkit-text-stroke:3px rgba(0,0,0,.40);paint-order:stroke fill;text-shadow:0 3px 14px rgba(0,0,0,.8),0 0 4px rgba(0,0,0,.7),0 6px 40px rgba(0,0,0,.5)}}"
      f".hook b{{color:{CY};font-weight:800}}"
      ".sub{position:absolute;top:1328px;left:0;right:0;text-align:center}"
      f".sub span{{display:inline-block;background:{PLATE};border-radius:14px;padding:12px 22px;font-weight:700;font-size:46px;line-height:1.05;color:#fff;white-space:nowrap}}"
      ".mark{position:absolute;top:248px;left:80px;font-weight:800;font-size:55px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.75),0 0 3px rgba(0,0,0,.6)}"
      f".mark b{{color:{CY}}}"
      f"</style></head><body>{body}</body></html>")
jobs = json.loads(sys.argv[1])
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width':1080,'height':1920})
    for name, hook, sub, top in jobs:
        body = ('<div style="position:absolute;left:0;right:0;top:760px;height:640px;background:linear-gradient(rgba(0,0,0,0),rgba(0,0,0,.38) 35%,rgba(0,0,0,.38) 65%,rgba(0,0,0,0))"></div>' if name=='ovA' else '') + '<div class=mark>Surf<b>Tribe</b></div>' + f'<div class=hook>{hook}</div>' + (f'<div class=sub><span>{sub}</span></div>' if sub else '')
        pg.set_content(page(body, top)); pg.wait_for_timeout(200)
        pg.screenshot(path=f'/tmp/en/ov/{name}.png', omit_background=True)
    b.close()
