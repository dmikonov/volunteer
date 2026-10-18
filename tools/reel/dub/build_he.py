"""Hebrew rebuild of a stock-footage tips reel, voice first: the voice track sets the cut points,
clean source clips are cut to it, captions are drawn in the English reel's style.
usage: python3 build_he.py spec.json   -> <out>/reel.mp4"""
import json, os, sys, base64, subprocess as sp
import numpy as np, cv2
from playwright.sync_api import sync_playwright

S = json.load(open(sys.argv[1])); O = S['out']; os.makedirs(f'{O}/ov', exist_ok=True); os.makedirs(f'{O}/sh', exist_ok=True)
W, H, FPS = 1080, 1920, 30
CY = '#00CDFC'; PLATE = 'rgba(20,20,28,.70)'
F = base64.b64encode(open('/s17/Rubik.ttf', 'rb').read()).decode()
WD = S['words'] if 'words' in S else json.load(open(S['words_file']))   # [[word, start, end], ...] on the final voice track
VO_T = float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', S['vo']], capture_output=True, text=True).stdout)
T = round(WD[-1][2] + S.get('tail', 0.7), 3)
wt = lambda i: WD[i][1]


def dur(f):
    return float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)


# ---------- shots (cut ~0.08 s before the word that starts each one) ----------
shots = S['shots']
for i, s in enumerate(shots):
    s['a'] = 0.0 if i == 0 else round(wt(s['at']) - 0.08, 3)
for i, s in enumerate(shots):
    s['b'] = shots[i + 1]['a'] if i + 1 < len(shots) else T
    s['d'] = round(s['b'] - s['a'], 3)
    if s['ss'] == 'cont': s['ss'] = round(shots[i - 1]['ss'] + shots[i - 1]['d'], 3)
parts = []
for i, s in enumerate(shots):
    src = s['src']; sd = dur(src); need = s['d'] + 0.1
    spd = 1.0
    if s['ss'] + need > sd:
        avail = sd - s['ss'] - 0.05
        spd = max(0.7, avail / need) if avail > 0 else 1.0
        if s['ss'] + need * spd > sd: s['ss'] = max(0.0, sd - need * spd - 0.05)
    z = s.get('zoom', 1.0); fx = s.get('x', 0.5); fy = s.get('y', 0.5)
    # crop a 9:16 window: height = ih/z, width = height*9/16, centered at fx,fy
    crop = (f"crop=w='min(iw,ih/{z}*9/16)':h='ih/{z}':x='(iw-min(iw,ih/{z}*9/16))*{fx}':y='(ih-ih/{z})*{fy}'")
    slow = f"setpts=(PTS-STARTPTS)/{spd}," if spd < 0.999 else 'setpts=PTS-STARTPTS,'
    fn = f'{O}/sh/{i:02d}.mp4'
    sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['ss']:.3f}", '-i', src, '-t', f'{need * spd + 0.1:.3f}', '-an',
            '-vf', f"{slow}{crop},scale={W}:{H}:flags=lanczos,fps={FPS},trim=duration={s['d']:.3f},setpts=PTS-STARTPTS" + (',' + s['eq'] if s.get('eq') else ''),
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', fn], check=True)
    parts.append(fn)
    print('shot', i, s.get('key'), s['a'], s['d'], 'spd', round(spd, 2))
open(f'{O}/sh/list.txt', 'w').write(''.join(f"file '{p}'\n" for p in parts))
sp.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{O}/sh/list.txt', '-c', 'copy', f'{O}/cut.mp4'], check=True)


# ---------- caption layers ----------
def page(body):
    return (f"<!doctype html><html><head><meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{F});font-weight:300 900}}"
            f"html,body{{margin:0;width:{W}px;height:{H}px;background:transparent;overflow:hidden}}*{{font-family:R;box-sizing:border-box}}"
            f".hook{{position:absolute;top:880px;right:70px;white-space:nowrap;direction:rtl;text-align:right;font-weight:900;font-size:104px;line-height:1.02;color:#fff;text-shadow:0 4px 22px rgba(0,0,0,.55)}}"
            f".hook b{{color:{CY};font-weight:900}}"
            f".pl{{position:absolute;top:1000px;right:60px;direction:rtl;display:flex;align-items:center;gap:22px;background:{PLATE};border-radius:22px;padding:22px 30px}}"
            f".n{{flex:none;width:80px;height:80px;border-radius:50%;background:{CY};color:#101418;font-weight:800;font-size:54px;line-height:80px;text-align:center}}"
            ".t{font-weight:800;font-size:64px;line-height:1.08;color:#fff;white-space:nowrap;text-align:right}"
            f".t b{{color:{CY};font-weight:800}}"
            ".sub{position:absolute;top:1328px;left:0;right:0;text-align:center;direction:rtl}"
            f".sub span{{display:inline-block;background:{PLATE};border-radius:16px;padding:14px 24px;font-weight:700;font-size:42px;line-height:1;color:#fff;white-space:nowrap}}"
            ".mark{position:absolute;top:262px;left:60px;direction:ltr;font-weight:800;font-size:46px;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.5)}"
            f".mark b,.end b{{color:{CY}}}"
            f".end{{position:absolute;top:600px;left:0;right:0;text-align:center;direction:ltr}}"
            f".end span{{display:inline-block;background:{PLATE};border-radius:22px;padding:22px 34px;font-weight:800;font-size:76px;line-height:1;color:#fff}}"
            f"</style></head><body>{body}</body></html>")


def crop_rgba(fn):
    im = cv2.imread(fn, cv2.IMREAD_UNCHANGED)
    ys, xs = np.where(im[:, :, 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    c = im[y0:y1, x0:x1].astype(np.float32)
    return {'x': int(x0), 'y': int(y0), 'rgb': c[:, :, [2, 1, 0]], 'a': c[:, :, 3:4] / 255.0}


layers = []  # (start, end, img, fade_in, fade_out, slide)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': W, 'height': H})

    def render(html, name):
        pg.set_content(page(html)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(80)
        pg.evaluate("() => { for (const t of document.querySelectorAll('.t,.hook')) { let f = parseFloat(getComputedStyle(t).fontSize); const mx = t.classList.contains('hook') ? 900 : 700; while (t.scrollWidth > mx && f > 36) { f -= 2; t.style.fontSize = f + 'px'; } } }")
        fn = f'{O}/ov/{name}.png'; pg.screenshot(path=fn, omit_background=True); return crop_rgba(fn)

    sh = {s['key']: s for s in shots}
    for i, t in enumerate(S['titles']):
        s = sh[t['shot']]; a = s['a'] + t.get('delay', 0.05); e = sh[t.get('until', t['shot'])]['b']
        l2 = f"<br><b>{t['l2']}</b>" if t.get('l2') else ''
        if t.get('hook'):
            img = render(f"<div class=hook>{t['l1']}{l2}</div>", f'title{i}')
            layers.append((0.0, e, img, 0.0, 0.0, 0))
        else:
            num = f"<div class=n>{t['n']}</div>" if t.get('n') else ''
            img = render(f"<div class=pl>{num}<div class=t>{t['l1']}{l2}</div></div>", f'title{i}')
            layers.append((a, e, img, 0.14, 0.0, 18))
    subs = S['subs']
    for i, (wi, txt) in enumerate(subs):
        a = wt(wi) - 0.05; e = (wt(subs[i + 1][0]) - 0.05) if i + 1 < len(subs) else T
        layers.append((max(0.0, a), e, render(f"<div class=sub><span>{txt}</span></div>", f'sub{i}'), 0.0, 0.0, 0))
    if S.get('mark'):
        layers.append((0.0, S['mark'], render("<div class=mark>Surf<b>Tribe</b></div>", 'mark'), 0.0, 0.25, 0))
    if S.get('end_at') is not None:
        layers.append((wt(S['end_at']) - 0.1, T, render("<div class=end><span>Surf<b>Tribe</b></span></div>", 'end'), 0.18, 0.0, 14))
    b.close()


def paste(fr, im, al, dy):
    x, y = im['x'], im['y'] + dy; h, w = im['a'].shape[:2]
    reg = fr[y:y + h, x:x + w].astype(np.float32); a = im['a'] * al
    fr[y:y + h, x:x + w] = (reg * (1 - a) + im['rgb'] * a).astype(np.uint8)


dec = sp.Popen(['ffmpeg', '-v', 'error', '-i', f'{O}/cut.mp4', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=sp.PIPE)
enc = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', f'{O}/v.mp4'], stdin=sp.PIPE)
n = 0; FS = W * H * 3
while True:
    buf = dec.stdout.read(FS)
    if len(buf) < FS: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy(); t = n / FPS
    for a, e, img, fi, fo, sl in layers:
        if a <= t < e:
            al = 1.0
            if fi: al = min(al, (t - a) / fi)
            if fo: al = min(al, (e - t) / fo)
            al = max(0.0, min(1.0, al))
            dy = int(round(sl * (1 - al) ** 2)) if sl else 0
            paste(fr, img, al, dy)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', n, 'T', T)

# ---------- audio: voice + looped music bed with gentle ducking ----------
r = sp.run(['ffmpeg', '-hide_banner', '-i', S['vo'], '-af', 'loudnorm=I=-15:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = f"loudnorm=I=-15:TP=-2:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
G = S.get('music_gain_db', 10.5)
afc = (f"[0:a]{ln},aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={T}[v0];[v0]asplit=2[vo][k0];"
       f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={G}dB,atrim=0:{T + 1.5},afade=t=out:st={T - 0.6:.2f}:d=0.6[mu];"
       f"[k0]apad=whole_dur={T + 2}[key];"
       f"[mu][key]sidechaincompress=threshold=0.06:ratio=2.5:attack=25:release=350,atrim=0:{T}[md];"
       f"[vo][md]amix=inputs=2:normalize=0:duration=longest,atrim=0:{T},volume=-1.5dB,alimiter=limit=0.84[aout]")
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', S['vo'], '-stream_loop', '-1', '-i', S['music'], '-filter_complex', afc, '-map', '[aout]', f'{O}/mix.wav'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{O}/mix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(r.split('I:')[-1].split('LUFS')[0]); g = round(-14.5 - I, 2)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{O}/v.mp4', '-i', f'{O}/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
        '-af', f'volume={g}dB,alimiter=limit=0.84:level=false', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', f'{O}/reel.mp4'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{O}/reel.mp4', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print('final', r.split('Summary:')[-1].replace('\n', ' ')[:300])
