"""Render the SurfTribe forecast screen (recreated from the app code) to frames/video.
usage: python3 record.py cfg.json out.mp4 [--still out.png --at SEC]
cfg: {lang, skill, day, hour, minute, clock, spot, focus, scrollAt, hlAt, dur, data(path)}
"""
import json, sys, os, subprocess, tempfile, pathlib
from playwright.sync_api import sync_playwright
D = pathlib.Path(__file__).parent
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
cfg['data'] = json.load(open(cfg['data'])) if isinstance(cfg['data'], str) else cfg['data']
cfg['dict'] = json.load(open(D / 'dict.json')); cfg['icons'] = json.load(open(D / 'icons.json'))
still = '--still' in sys.argv
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=1080 / 390)
    pg.add_init_script('window.CFG=' + json.dumps(cfg, ensure_ascii=False))
    pg.goto('file://' + str(D / 'forecast.html')); pg.wait_for_function('window.READY===true'); pg.wait_for_timeout(400)
    meta = pg.evaluate('window.META'); print(json.dumps(meta, ensure_ascii=False))
    if still:
        pg.evaluate(f"setT({float(sys.argv[sys.argv.index('--at') + 1])})"); pg.screenshot(path=sys.argv[sys.argv.index('--still') + 1])
    else:
        tmp = tempfile.mkdtemp(); fps = 30; n = int(cfg.get('dur', 7) * fps)
        for i in range(n):
            pg.evaluate(f'setT({i / fps})'); pg.screenshot(path=f'{tmp}/f{i:04d}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', f'{tmp}/f%04d.png', '-vf', 'scale=1080:-2', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', out], check=True)
        import shutil; shutil.rmtree(tmp, ignore_errors=True)
    b.close()
