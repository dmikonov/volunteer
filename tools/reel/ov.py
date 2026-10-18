import json, os, sys, re, base64, subprocess as sp
import cv2, numpy as np
from playwright.sync_api import sync_playwright
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); LANG = S['lang']; HE = LANG == 'he'; A = '/s17/tip1'
TL = json.load(open(f'{W}/tl.json')); L = TL['L']; T = TL['T']
segs = json.load(open(f'{W}/segs.json'))
cuts = [0.0] + [round(l['t0'] - 0.1, 3) for l in L[1:]] + [T]
CY, AM, NAVY, RED, GRN = '#00d4ff', '#f5a623', 'rgba(10,18,38,.80)', '#FF5150', '#3DDC84'
XI = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{RED}'/><path d='M20 20L44 44M44 20L20 44' stroke='#fff' stroke-width=8 stroke-linecap=round/></svg>"
CK = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{GRN}'/><path d='M17 33L28 44L47 22' stroke='#fff' stroke-width=8 fill=none stroke-linecap=round stroke-linejoin=round/></svg>"
WARN = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{RED}'/><path d='M32 14V38' stroke='#fff' stroke-width=8 stroke-linecap=round/><circle cx=32 cy=49 r=5 fill='#fff'/></svg>"
ICON = {'X': XI, 'CK': CK, 'WARN': WARN, None: None}
TITLES = S['titles']; RECAP = S['recap']; LAST = L[-1]['k']
F = base64.b64encode(open('/s17/Rubik.ttf', 'rb').read()).decode()
DIR = 'rtl' if HE else 'ltr'; FS = 80 if HE else 70
def page(body):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{F});font-weight:300 900}}
html,body{{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}}*{{font-family:R;box-sizing:border-box}}
.blk{{position:absolute;top:330px;left:0;right:0;text-align:center;direction:{DIR};transform-origin:50% 40%}}
.plate{{display:inline-block;white-space:nowrap;padding:26px 34px;border-radius:26px;background:{NAVY};font-weight:800;font-size:{FS}px;line-height:1.15;text-box:trim-both cap alphabetic;color:#fff}}
.plate.sm{{font-size:{62 if HE else 56}px}}
.n{{display:inline-block;width:92px;height:92px;border-radius:50%;background:{CY};color:#0a1226;font-weight:800;font-size:62px;line-height:92px;text-align:center;margin-bottom:14px}}
.sub{{position:absolute;top:1298px;left:0;right:0;text-align:center;direction:{DIR}}}
.sub span{{display:inline-block;white-space:nowrap;padding:18px 28px;border-radius:20px;background:{NAVY};font-weight:800;font-size:50px;line-height:1;text-box:trim-both cap alphabetic;color:#fff}}
.mark{{position:absolute;top:240px;left:0;right:0;text-align:center;direction:ltr}}
.mark span.b{{display:inline-block;padding:16px 26px;border-radius:20px;background:{NAVY};font-weight:800;font-size:48px;line-height:1;text-box:trim-both cap alphabetic;color:#fff}}
.rc{{position:absolute;top:330px;left:0;right:0;text-align:center;direction:{DIR}}}
.rc .box{{display:inline-block;width:620px;padding:26px 34px 30px;border-radius:30px;background:{NAVY};text-align:{'right' if HE else 'left'}}}
.rc h{{display:block;font-weight:800;font-size:{58 if HE else 50}px;color:{CY};margin-bottom:18px;text-align:center}}
.rc .row{{font-weight:800;font-size:{52 if HE else 44}px;color:#fff;margin:12px 0;white-space:nowrap}}
</style></head><body>{body}</body></html>"""
if S.get('app_notitle'):
    for kk in S.get('app_lines', []): TITLES.pop(kk, None)
cards = {}
for l in L:
    if l['k'] == LAST or l['k'] not in TITLES: continue
    a, b, n, ic = TITLES[l['k']]; ic = ICON[ic]
    num = f"<div class=n>{n}</div><br>" if n else ''
    acc = AM if l['k'] in ('L1', 'L2') else CY
    icon = f"{ic}&nbsp;" if ic else ''
    sm = ' sm' if l['k'] in S.get('app_lines', []) else ''
    inner = f"{num}<div class='plate{sm}'>{icon}{a}<br><span style='color:{acc}'>{b}</span></div>"
    for tag, sc in (('a', 1.22), ('b', 0.95), ('c', 1.0)):
        top = f"top:{S.get('app_top', 330)}px;" if sm else ''
        cards[f"T{l['k']}{tag}"] = f"<div class=blk style='{top}transform:scale({sc})'>{inner}</div>"
rows = ''.join(f"<div class=row>{CK}&nbsp;&nbsp;{x}</div>" for x in RECAP[1])
for tag, sc in (('a', 1.15), ('b', 0.97), ('c', 1.0)):
    cards[f'RECAP{tag}'] = f"<div class=rc style='transform:scale({sc});transform-origin:50% 30%'><div class=box><h>{RECAP[0]}</h>{rows}</div></div>"
cards['MARK'] = f"<div class=mark><span class=b>Surf<span style='color:{CY}'>Tribe</span></span></div>"
cards['MARKA'] = f"<div class=mark style='top:{S.get('app_top', 330) - 90}px'><span class=b>Surf<span style='color:{CY}'>Tribe</span></span></div>"
cards['FLASH'] = "<div style='position:absolute;inset:0;background:rgba(255,255,255,.85)'></div>"
STOP = {'עם', 'על', 'את', 'של', 'לפני', 'the', 'a', 'to', 'of', 'with', 'your', 'from', 'and', 'at', 'over', 'when', 'you', 'is', 'off', 'on', 'in', 'by'}
subs = []
for l in L:
    toks = l['txt'].split(); Wd = l['words']
    if len(toks) != len(Wd): toks = [w[0] for w in Wd]
    phrases, curp = [], []
    for tok, w in zip(toks, Wd):
        curp.append((tok, w[1], w[2]))
        if tok.endswith(('.', ',', ':')): phrases.append(curp); curp = []
    if curp: phrases.append(curp)
    for ph in phrases:
        if len(ph) <= 4: subs.append([' '.join(c[0] for c in ph), ph[0][1], ph[-1][2]]); continue
        best = None
        for cut in sorted(range(1, len(ph)), key=lambda c: abs(len(' '.join(x[0] for x in ph[:c])) - len(' '.join(x[0] for x in ph[c:])))):
            if ph[cut - 1][0].strip('.,:').lower() not in STOP: best = cut; break
        best = best or len(ph) // 2
        for part in (ph[:best], ph[best:]): subs.append([' '.join(c[0] for c in part), part[0][1], part[-1][2]])
clean = []
for i, (txt, s0, s1) in enumerate(subs):
    nxt = subs[i + 1][1] if i + 1 < len(subs) else s1 + 0.4
    lend = min([c for c in cuts if c > s0 + 0.05] + [T]) - 0.04
    tx = re.sub(r'[.,:]$', '', txt.strip())
    for k0, v0 in S.get('sub_replace', {}).items(): tx = tx.replace(k0, v0)
    clean.append((tx, s0, min(nxt, s1 + 0.5, lend)))
APPW = [(cuts[[l['k'] for l in L].index(kk)], cuts[[l['k'] for l in L].index(kk) + 1]) for kk in S.get('app_lines', [])]
for i, (txt, s0, s1) in enumerate(clean):
    st = f" style='top:{S['app_sub_top']}px'" if S.get('app_sub_top') and any(a0 - 0.05 <= s0 < b0 for a0, b0 in APPW) else ''
    cards[f'S{i:02d}'] = f"<div class=sub{st}><span>{txt}</span></div>"
os.makedirs(f'{W}/ov', exist_ok=True); pos = {}; boxes = {}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    for k, h in cards.items():
        pg.set_content(page(h)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(100)
        pg.evaluate("() => { for (const [sel, mx] of [['.sub span', 600], ['.plate', 620]]) for (const e of document.querySelectorAll(sel)) { let f = parseFloat(getComputedStyle(e).fontSize); while (e.getBoundingClientRect().width > mx && f > 24) { f -= 2; e.style.fontSize = f + 'px'; } } }")
        boxes[k] = pg.evaluate("() => [...document.querySelectorAll('.plate,.sub span,.mark span.b,.n,.rc .box')].map(e => {const r=e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom)]})")
        fn = f'{W}/ov/{k}.png'; pg.screenshot(path=fn, omit_background=True)
        im = cv2.imread(fn, cv2.IMREAD_UNCHANGED); ys, xs = (im[..., 3] > 0).nonzero()
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1; cv2.imwrite(fn, im[y0:y1, x0:x1]); pos[k] = (int(x0), int(y0))
    br.close()
bad = [(k, b) for k, bb in boxes.items() if not k.endswith(('a', 'b')) for b in bb if b[0] < 70 or b[1] > 850 or b[2] < 230 or b[3] > 1440]
print('safe-zone violations', bad)
ON = []; F1, F2 = 0.08, 0.16
for i, l in enumerate(L):
    a, b = cuts[i], cuts[i + 1]
    base = 'RECAP' if l['k'] == LAST else ('T' + l['k'] if l['k'] in TITLES else None)
    if base: ON += [(base + 'a', a, a + F1), (base + 'b', a + F1, a + F2), (base + 'c', a + F2, b)]
    if i > 0: ON.append(('FLASH', a - 0.02, a + 0.06))
ON += [('MARK', 0, 3.0), ('MARK', cuts[-2], T)]
for kk in S.get('app_lines', []):
    i = [l['k'] for l in L].index(kk)
    if not S.get('app_notitle'): ON.append(('MARKA', cuts[i], cuts[i + 1]))
ON += [(f'S{i:02d}', s0, s1) for i, (txt, s0, s1) in enumerate(clean)]
wh = [round(c - 0.22, 3) for c in cuts[1:-1]]
imp = [round(s['t0'] + s['shk'][0], 3) for s in segs if s.get('shk')]
pops = [round(cuts[i] + 0.05, 3) for i, l in enumerate(L)]
ains = ['-i', f'{W}/vo.wav', '-stream_loop', '-1', '-i', f'{A}/music.wav']
MV = S.get('music_vol', 0.9)  # Dima 18.10: music was inaudible at 0.30
afc = [f"[1:a]volume={MV},atrim=0:{T},afade=t=in:d=0.3,afade=t=out:st={max(0, T - 1.2):.2f}:d=1.2[mu]", "[0:a]asplit=2[vo][k0]", f"[k0]apad=whole_dur={T + 1}[key]", "[mu][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[md]"]  # apad: reviewer 18.10, music was cut 0.6 s early
mixin = ['[vo]', '[md]']; k = 2
for fn, times, vol in (('whoosh.wav', wh, 0.55), ('impact.wav', imp, 0.8), ('pop.wav', pops, 0.45)):
    for tt in times:
        ains += ['-i', f'{A}/{fn}']; afc.append(f"[{k}:a]adelay={int(max(0, tt) * 1000)}|{int(max(0, tt) * 1000)},volume={vol}[x{k}]"); mixin.append(f'[x{k}]'); k += 1
afc.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:duration=longest,atrim=0:{T},volume=-1.6dB,alimiter=limit=0.84[aout]")  # ~-14.5 LUFS, <= -1.5 dBTP
sp.run(['ffmpeg', '-v', 'error', '-y'] + ains + ['-filter_complex', ';'.join(afc), '-map', '[aout]', '-t', str(T), '-ar', '48000', '-ac', '2', f'{W}/mix.wav'], check=True)
ins = ['-i', f'{W}/cat.mp4', '-i', f'{W}/mix.wav']; fcs = []; prev = '0:v'
for i, (kk, a, b) in enumerate(ON):
    # each image exists only inside its window: decode cost ~ window length, not the whole reel
    ins += ['-loop', '1', '-framerate', '25', '-t', f'{max(0.04, b - a):.3f}', '-i', f'{W}/ov/{kk}.png']
    fcs.append(f"[{i + 2}:v]format=rgba,setpts=PTS+{a:.3f}/TB[o{i}]")
    fcs.append(f"[{prev}][o{i}]overlay={pos[kk][0]}:{pos[kk][1]}:eof_action=pass:repeatlast=0[v{i}]"); prev = f'v{i}'
OUT = f"{W}/{S['out']}"
sp.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fcs), '-map', f'[{prev}]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-maxrate', '18M', '-bufsize', '36M', '-pix_fmt', 'yuv420p', '-r', '25', '-c:a', 'aac', '-b:a', '192k', '-t', str(T), '-movflags', '+faststart', OUT], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', OUT, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); g = round(-14.5 - I, 2)  # reviewer 18.10: -14.5 LUFS, true peak <= -1.5 dBTP
if abs(g) > 0.2:
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT, '-c:v', 'copy', '-af', f'volume={g}dB,alimiter=limit=0.84', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT + '.t.mp4'], check=True); os.replace(OUT + '.t.mp4', OUT)
print('done', OUT, T, 'lufs before', I, 'gain', g)
