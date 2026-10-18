"""Generic reel builder. usage: python3 build.py <workdir>   (workdir has spec.json, tl.json)
spec.plan: {"L1": [seg, ...], ...}; seg = {"src": "C0188"|"/path.mp4", "a": float, "z": zoom, "cx": [x0,x1], "cy": [y0,y1],
            "shk": [t0,t1] | null, "frz": sec, "dd": fixed duration | null, "kind": "raw"|"gen"|"app"}
"""
import json, os, sys, subprocess as sp
import cv2, numpy as np
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); TL = json.load(open(f'{W}/tl.json')); L = TL['L']; T = TL['T']
def dur(f):
    r = sp.run(['ffmpeg', '-hide_banner', '-i', f], capture_output=True, text=True).stderr
    h, m, s = r.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
cuts = [0.0] + [round(l['t0'] - 0.1, 3) for l in L[1:]] + [T]
segs = []; t_out = 0.0
for i, l in enumerate(L):
    D0 = cuts[i + 1] - cuts[i]; E = S['plan'][l['k']]; n = len(E); acc = 0
    for j, e in enumerate(E):
        dd = e.get('dd'); frz = e.get('frz', 0)
        d = (dd if dd else round(D0 / n, 3)) if j < n - 1 else round(D0 - acc, 3); acc += d
        dm = round(d - frz, 3)
        kind = e.get('kind', 'raw'); src = e['src'] if kind != 'raw' else f"/s17/raw/{e['src']}.MP4"
        if kind == 'raw' and e.get('stab', True) and os.path.exists(f"/s17/raw_stab/{e['src']}.MP4"): src = f"/s17/raw_stab/{e['src']}.MP4"  # Dima 18.10: stabilized
        spd = e.get('spd', 1.0)  # <1 = slow motion
        a = e['a']
        if isinstance(a, list): a = round(a[1] - dm * spd, 3)  # ["end", t]
        sd = dur(src); sdur = round(dm * spd, 3)
        if a + sdur > sd - 0.04:  # not enough source: freeze the tail
            extra = round(a + sdur - (sd - 0.04), 3); sdur = round(sdur - extra, 3); dm = round(sdur / spd, 3); frz = round(d - dm, 3)
        assert a >= 0 and dm > 0.2, (l['k'], e, a, dm, sd)
        segs.append(dict(e, kind=kind, srcp=src, a=a, d=d, dm=dm, sdur=sdur, spd=spd, frz=frz, line=l['k'], t0=round(t_out, 3))); t_out += d
print([(s['line'], s['src'][-12:], s['a'], s['d'], s['t0']) for s in segs])
os.makedirs(f'{W}/seg', exist_ok=True); lst = []
for i, s in enumerate(segs):
    z = s.get('z', 1.0); cx0, cx1 = s.get('cx', [.5, .5]); cy0, cy1 = s.get('cy', [.5, .5]); SD = s['dm']
    X = f"max(0\\,min(iw-iw/{z}\\,({cx0}+({cx1}-{cx0})*t/{SD})*iw-iw/{z}/2))"; Y = f"max(0\\,min(ih-ih/{z}\\,({cy0}+({cy1}-{cy0})*t/{SD})*ih-ih/{z}/2))"
    frz = f",tpad=stop_mode=clone:stop_duration={s['frz'] + 0.1}" if s['frz'] else ''
    shake = ''
    if s.get('shk'):
        A, B = s['shk']; shake = f",crop=1032:1835:'24+22*sin(t*63)*between(t,{A},{B})':'42+20*sin(t*51+1)*between(t,{A},{B})',scale=1080:1920"
    if s['kind'] == 'raw':
        cap = cv2.VideoCapture(s['srcp']); fps = cap.get(5); accm = []
        for tt in np.linspace(s['a'], s['a'] + s['sdur'] - 0.1, 3):
            cap.set(1, int(tt * fps)); ok, fr = cap.read(); accm.append(cv2.resize(fr, (480, 270)).astype(np.float32).reshape(-1, 3).mean(0))
        b, g, r = np.mean(accm, 0); m = (b + g + r) / 3; wbk = .7 if s['src'] in ('C0170', 'C0175') else .35
        gr, gg, gb = [1 + wbk * (m / c - 1) for c in (r, g, b)]
        eq = 'eq=contrast=1.32:saturation=1.22:gamma=0.72:brightness=-0.07' if s['src'] in ('C0170', 'C0175') else ('eq=contrast=1.12:saturation=1.15:gamma=0.92' if m > 200 else 'eq=contrast=1.08:saturation=1.15:gamma=0.98')
        pre = 'transpose=1,'; post = f",colorchannelmixer=rr={gr:.3f}:gg={gg:.3f}:bb={gb:.3f},{eq}"
    elif s['kind'] == 'gen':
        pre = ''; post = ',eq=contrast=1.04:saturation=1.05'
    else:  # app screen: keep colors
        pre = ''; post = ''
    # crop to 9:16 window first (sources may be taller than 9:16), then zoom
    ar = "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)':'(iw-min(iw,ih*9/16))/2':'" + ("(ih-min(ih,iw*16/9))*" + str(s.get('ay', 0.5))) + "',"
    slow = f"setpts=(PTS-STARTPTS)/{s['spd']}," if s['spd'] != 1.0 else ''
    vf = f"{slow}{pre}{ar}crop=iw/{z}:ih/{z}:'{X}':'{Y}',scale=1080:1920:flags=lanczos{post}{shake},fps=25{frz},setsar=1"
    o = f'{W}/seg/{i:02d}.mp4'; key = json.dumps([s['srcp'], s['a'], s['d'], s['dm'], s['sdur'], s['frz'], vf]); kf = o + '.key'
    if os.path.exists(o) and os.path.exists(kf) and open(kf).read() == key: lst.append(o); continue
    sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s['a']), '-t', str(round(s['sdur'] + 0.06, 3)), '-i', s['srcp'], '-vf', vf + f",trim=duration={s['d']}", '-an', '-threads', '1', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', o], check=True); lst.append(o); open(kf, 'w').write(key)
open(f'{W}/seg/list.txt', 'w').write(''.join(f"file '{x}'\n" for x in lst))
sp.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{W}/seg/list.txt', '-vf', 'fps=25,format=yuv420p', '-threads', '1', '-c:v', 'libx264', '-preset', 'fast', '-x264-params', 'rc-lookahead=10', '-crf', '15', f'{W}/cat.mp4'], check=True)
json.dump(segs, open(f'{W}/segs.json', 'w'))
print('cat', dur(f'{W}/cat.mp4'), 'T', T)
