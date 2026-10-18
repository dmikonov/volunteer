"""Re-voice a finished reel in another language: cover the burned-in captions with frosted cards,
render new titles + subtitles, lay a new voice over the separated music bed.
usage: python3 dub.py spec.json            (outputs <out>/dub.mp4)"""
import json, os, sys, base64, subprocess as sp
import numpy as np, cv2
from playwright.sync_api import sync_playwright

S = json.load(open(sys.argv[1])); O = S['out']; os.makedirs(f'{O}/ov', exist_ok=True)
W, H, FPS = 1080, 1920, 30
CY, NAVY = '#00d4ff', (10, 18, 38)
F = base64.b64encode(open('/s17/Rubik.ttf', 'rb').read()).decode()
WT = json.load(open(S['wt']))
VO = {k: t for k, t in S['vo']}
SRC_T = float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', S['src']], capture_output=True, text=True).stdout)
SF, SL = S['slow_from'], S['slow']
SE = S.get('src_end', SRC_T)
T = round(SF + (SE - SF) / SL, 3)
STEP = (36, 984, 876, 1238); HOOK = (36, 900, 876, 1250)
SUB_Y0, SUB_Y1, SUB_MIN = 1316, 1408, 680


def page(body):
    return (f"<!doctype html><html><head><meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{F});font-weight:300 900}}"
            f"html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}*{{font-family:R;box-sizing:border-box}}"
            ".card{position:absolute;display:flex;align-items:center;justify-content:flex-start;direction:rtl;padding:0 40px;gap:26px}"
            f".n{{flex:none;width:96px;height:96px;border-radius:50%;background:{CY};color:#0a1226;font-weight:800;font-size:62px;line-height:96px;text-align:center}}"
            ".t{font-weight:800;color:#fff;line-height:1.12;white-space:nowrap;text-align:right}"
            f".t b{{color:{CY};font-weight:800}}"
            ".sub{position:absolute;left:0;right:0;text-align:center;direction:rtl}"
            ".sub span{display:inline-block;white-space:nowrap;font-weight:800;font-size:48px;line-height:1;color:#fff}"
            f"</style></head><body>{body}</body></html>")


def crop_rgba(fn):
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    ys, xs = np.where(im[:, :, 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    c = im[y0:y1, x0:x1].astype(np.float32)
    rgb = c[:, :, [2, 1, 0]]; a = c[:, :, 3:4] / 255.0
    return {'x': int(x0), 'y': int(y0), 'rgb': rgb, 'a': a}


# ---------- render text layers ----------
titles, subs = [], []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})

    def shot(html, fn):
        pg.set_content(page(html)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(80)
        pg.screenshot(path=fn, omit_background=True)

    for i, t in enumerate(S['titles']):
        x0, y0, x1, y1 = HOOK if t.get('hook') else STEP
        fs = 88 if t.get('hook') else 74
        num = f"<div class=n>{t['n']}</div>" if t.get('n') else ''
        l2 = f"<br><b>{t['l2']}</b>" if t.get('l2') else ''
        html = f"<div class=card style='left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px'>{num}<div class=t style='font-size:{fs}px'>{t['l1']}{l2}</div></div>"
        pg.set_content(page(html)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(80)
        pg.evaluate("() => { const c = document.querySelector('.card'), t = document.querySelector('.t'), n = document.querySelector('.n'); const mx = c.clientWidth - 80 - (n ? 122 : 0); let f = parseFloat(getComputedStyle(t).fontSize); while (t.scrollWidth > mx && f > 40) { f -= 2; t.style.fontSize = f + 'px'; } }")
        fn = f'{O}/ov/title{i}.png'; pg.screenshot(path=fn, omit_background=True)
        # shrink check: text must fit the card
        titles.append(dict(t, rect=(x0, y0, x1, y1), img=crop_rgba(fn)))
    for i, (k, wi, txt, *force) in enumerate(S['subs']):
        html = f"<div class=sub style='top:{SUB_Y0}px;height:{SUB_Y1 - SUB_Y0}px;line-height:{SUB_Y1 - SUB_Y0}px'><span id=s>{txt}</span></div>"
        pg.set_content(page(html)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(60)
        w = pg.evaluate("document.getElementById('s').getBoundingClientRect().width")
        fn = f'{O}/ov/sub{i}.png'; pg.screenshot(path=fn, omit_background=True)
        ws = WT[k]['w']; st = round(VO[k] + ws[min(wi, len(ws) - 1)][1], 3)
        if force: st = min(st, force[0])
        pw = max(SUB_MIN, int(w) + 70)
        subs.append({'t': st, 'txt': txt, 'rect': (540 - pw // 2, SUB_Y0, 540 + pw // 2, SUB_Y1), 'img': crop_rgba(fn)})
    b.close()
subs[0]['t'] = min(subs[0]['t'], S['sub_from'])
for i, s in enumerate(subs):
    s['e'] = subs[i + 1]['t'] if i + 1 < len(subs) else T
print('subs', [(s['txt'], s['t']) for s in subs])

# ---------- frame compositor ----------
_mask = {}


def rmask(w, h, r):
    k = (w, h, r)
    if k not in _mask:
        m = np.zeros((h * 4, w * 4), np.uint8)
        R = r * 4
        cv2.rectangle(m, (R, 0), (w * 4 - R, h * 4), 255, -1); cv2.rectangle(m, (0, R), (w * 4, h * 4 - R), 255, -1)
        for cx, cy in ((R, R), (w * 4 - R, R), (R, h * 4 - R), (w * 4 - R, h * 4 - R)): cv2.circle(m, (cx, cy), R, 255, -1)
        _mask[k] = (cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0)[:, :, None]
    return _mask[k]


NV = np.array(NAVY, np.float32)


def card(fr, rect, al, r=28, tint=0.93):
    x0, y0, x1, y1 = rect; p = 48
    X0, Y0, X1, Y1 = max(0, x0 - p), max(0, y0 - p), min(W, x1 + p), min(H, y1 + p)
    bl = cv2.GaussianBlur(fr[Y0:Y1, X0:X1], (0, 0), 28)[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0].astype(np.float32)
    c = bl * (1 - tint) + NV * tint
    m = rmask(x1 - x0, y1 - y0, r) * al
    reg = fr[y0:y1, x0:x1].astype(np.float32)
    fr[y0:y1, x0:x1] = (reg * (1 - m) + c * m).astype(np.uint8)


def paste(fr, im, al):
    x, y = im['x'], im['y']; h, w = im['a'].shape[:2]
    reg = fr[y:y + h, x:x + w].astype(np.float32); a = im['a'] * al
    fr[y:y + h, x:x + w] = (reg * (1 - a) + im['rgb'] * a).astype(np.uint8)


def ramp(t, a, b, fi=0.12, fo=0.0):
    if t < a or t >= b: return 0.0
    v = 1.0
    if fi: v = min(v, (t - a) / fi)
    if fo: v = min(v, (b - t) / fo)
    return max(0.0, min(1.0, v))


vf = (f"[0:v]split[a][b];[a]trim=end={SF},setpts=PTS-STARTPTS[a1];"
      f"[b]trim=start={SF}:end={SE},setpts=(PTS-STARTPTS)/{SL},minterpolate=fps={FPS}:mi_mode=blend[b1];"
      f"[a1][b1]concat=n=2:v=1:a=0,scale={W}:{H}:flags=lanczos,unsharp=5:5:0.35,fps={FPS},format=rgb24")
dec = sp.Popen(['ffmpeg', '-v', 'error', '-i', S['src'], '-filter_complex', vf, '-f', 'rawvideo', '-'], stdout=sp.PIPE)
enc = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', f'{O}/v.mp4'], stdin=sp.PIPE)
n = 0; FS = W * H * 3
last_t = S['titles'][-1]['b']
while True:
    buf = dec.stdout.read(FS)
    if len(buf) < FS: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); t = n / FPS
    for i, ti in enumerate(S['titles']):
        if ti['a'] <= t < ti['b']:
            ca = ramp(t, ti['a'], ti['b'], fi=0, fo=0.12 if ti['b'] == last_t else 0)
            card(fr, titles[i]['rect'], ca)
            paste(fr, titles[i]['img'], ca * ramp(t, ti['a'], ti['b'], fi=0.07 if i else 0))
    for s in subs:
        if s['t'] <= t < s['e']:
            card(fr, s['rect'], 1.0, r=22, tint=0.93); paste(fr, s['img'], 1.0)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', n, 'T', T)

# ---------- audio ----------
ins, fc = [], []
for i, (k, at) in enumerate(S['vo']):
    ins += ['-i', f"{S['vo_dir']}/{k}.wav"]
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(at * 1000)}:all=1[v{i}]")
fc.append(''.join(f'[v{i}]' for i in range(len(S['vo']))) + f"amix=inputs={len(S['vo'])}:normalize=0,apad=whole_dur={T}[vo]")
sp.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc), '-map', '[vo]', '-t', str(T), f'{O}/vo_raw.wav'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{O}/vo_raw.wav', '-af', 'loudnorm=I=-15:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = f"loudnorm=I=-15:TP=-2:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{O}/vo_raw.wav', '-af', f'{ln},aresample=48000', '-ac', '2', f'{O}/vo.wav'], check=True)
G = S['music_gain_db']
afc = (f"[1:a]aresample=48000,asplit[m1][m2];[m1][m2]acrossfade=d=0.4[mm];[mm]volume={G}dB,atrim=0:{T + 1.5},afade=t=out:st={T - 0.5:.2f}:d=0.5[mu];"
       "[0:a]asplit=2[vo][k0];"
       f"[k0]apad=whole_dur={T + 2}[key];"
       f"[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=350,atrim=0:{T}[md];"
       f"[vo][md]amix=inputs=2:normalize=0:duration=longest,atrim=0:{T},volume=-1.5dB,alimiter=limit=0.84[aout]")
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{O}/vo.wav', '-i', S['music'], '-filter_complex', afc, '-map', '[aout]', f'{O}/mix.wav'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{O}/mix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(r.split('I:')[-1].split('LUFS')[0]); g = round(-14.5 - I, 2)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{O}/v.mp4', '-i', f'{O}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
        '-af', f'volume={g}dB,alimiter=limit=0.84:level=false', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', f'{O}/dub.mp4'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{O}/dub.mp4', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print('final', r.split('Summary:')[-1].replace('\n', ' ')[:400])
