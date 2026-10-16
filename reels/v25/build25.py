"""Reel 25 'מי נופל ראשון?' for @surftribe_il. Real clip C0082 (two surfers on one wave), virtual camera,
flow-interpolated slow motion, freeze on the board in the air, Hebrew overlays from Chromium PNGs.
Timeline lives in tl.json (written by plan25.py from the measured VO durations)."""
import sys, json, os, subprocess as sp, math
import numpy as np, cv2
sys.path.insert(0, '/home/claude/work/prod/render'); sys.path.insert(0, '/home/claude/work/prod/design')
from interp2 import flows, interp
import design4 as d4

D = '/home/claude/work/series/reels/guess25'; OV = D + '/ov'; CACHE = D + '/src'
SRC = '/mnt/user-data/uploads/C0082.mp4'
W, H, FPS = 1080, 1920, 30
TL = json.load(open(D + '/tl.json'))
OUT = os.environ.get('OUTV', D + '/v25_silent.mp4')
ONLY = os.environ.get('ONLY')            # comma list of output frame numbers for stills

# ---------- source frame cache (full res, rotated upright)
os.makedirs(CACHE, exist_ok=True)
if not os.path.exists(CACHE + '/191.jpg'):
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-vf', 'transpose=2', '-q:v', '2', CACHE + '/%d.jpg'], check=True)
    for i in range(1, 193): os.rename(f'{CACHE}/{i}.jpg', f'{CACHE}/{i-1}.jpg')
_fc = {}
def frame(i):
    i = int(max(0, min(191, i)))
    if i not in _fc:
        if len(_fc) > 6: _fc.pop(next(iter(_fc)))
        im = cv2.imread(f'{CACHE}/{i}.jpg')
        if i in TL.get('blur', []): im = cv2.GaussianBlur(im, (0, 0), 5)   # source autofocus flicker: match the soft neighbours
        _fc[i] = im
    return _fc[i]

# ---------- rider tracks (from YOLO pose boxes)
trk = json.load(open('/tmp/claude-0/-home-claude/9af8fd2f-ee91-5254-9760-53eb87908abc/scratchpad/r25/trk.json'))
def pick(f, who):
    bs = [b for b in trk[f]['b'] if b['box'][2] - b['box'][0] > 100]
    if who == 'black':
        if f <= 31: bs = [b for b in bs if b['box'][0] > 1000]
        bs = [b for b in bs if b['v'] < 110 and f <= 74]
    else:
        bs = [b for b in bs if b['v'] >= 118 and f >= 34]
    if not bs: return None
    return max(bs, key=lambda b: b['box'][2] - b['box'][0])
def cands(f, who):
    bs = [b for b in trk[f]['b'] if b['box'][2] - b['box'][0] > 100]
    if who == 'black':
        if f <= 31: bs = [b for b in bs if b['box'][0] > 1000]
        return [b for b in bs if b['v'] < 110 and f <= 74]
    return [b for b in bs if b['v'] >= 118 and f >= 34]
def series(who):
    cx, cy, top, hh, knee = (np.full(192, np.nan) for _ in range(5)); last = None
    for f in range(192):
        bs = cands(f, who)
        if last is not None and bs:      # continuity: nearest box to the previous centre
            bs = [min(bs, key=lambda q: abs((q['box'][0] + q['box'][2]) / 2 - last[0]) + abs((q['box'][1] + q['box'][3]) / 2 - last[1]))]
            q = bs[0]; d = abs((q['box'][0] + q['box'][2]) / 2 - last[0])
            if d > 420: bs = []
        b = (max(bs, key=lambda q: q['box'][2] - q['box'][0]) if bs else None)
        if b is None: continue
        last = ((b['box'][0] + b['box'][2]) / 2, (b['box'][1] + b['box'][3]) / 2)
        x0, y0, x1, y1 = b['box']; cx[f] = (x0 + x1) / 2; cy[f] = (y0 + y1) / 2; top[f] = y0; hh[f] = y1 - y0
        k = [v for v in b['knee'] if v]
        if k: knee[f] = np.mean(k)
    return cx, cy, top, hh, knee
def fill(a):
    a = a.copy(); idx = np.arange(len(a)); ok = ~np.isnan(a)
    if ok.sum() == 0: return a
    return np.interp(idx, idx[ok], a[ok])
def smooth(a, s):
    k = np.exp(-0.5 * (np.arange(-3 * s, 3 * s + 1) / s) ** 2); k /= k.sum()
    p = np.pad(a, (3 * s, 3 * s), mode='edge'); return np.convolve(p, k, 'valid')
BL = [fill(x) for x in series('black')]; PK = [fill(x) for x in series('pink')]
BLK = smooth(fill(series('black')[4]), 2)
black_seen = ~np.isnan(series('black')[0]); pink_seen = ~np.isnan(series('pink')[0])

# ---------- time map: output frame -> source frame position
segs = TL['segs']          # [{'a':srcA,'b':srcB,'dur':sec}] ; a==b is a freeze
T_TOTAL = sum(s['dur'] for s in segs); NOUT = int(round(T_TOTAL * FPS))
def src_pos(t):
    acc = 0.0
    for s in segs:
        if t < acc + s['dur'] or s is segs[-1]:
            u = min(max((t - acc) / s['dur'], 0), 1); return s['a'] + (s['b'] - s['a']) * u, s
        acc += s['dur']
def seg_start(name):
    acc = 0.0
    for s in segs:
        if s.get('name') == name: return acc
        acc += s['dur']

# ---------- virtual camera, computed on the output timeline then smoothed
cam = np.zeros((NOUT, 3))     # cx, cy, crop width
for k in range(NOUT):
    p, s = src_pos(k / FPS); f = int(round(p)); mode = s['cam']
    if mode == 'both' and pink_seen[min(f + 2, 191)]:
        x0 = min(BL[0][f], PK[0][f]); x1 = max(BL[0][f], PK[0][f])
        cx = (x0 + x1) / 2; cy = (BL[1][f] + PK[1][f]) / 2; w = np.clip(x1 - x0 + 760, 1150, 1700)
    elif mode in ('both', 'black'):
        cx, cy, w = BL[0][min(f, 72)], BL[1][min(f, 72)], s.get('w', 1150)
    else:
        ff = min(f, 158); cx, cy, w = PK[0][ff], PK[1][ff], s.get('w', 1100)
    cam[k] = cx, cy, w
for j in range(3): cam[:, j] = smooth(cam[:, j], 7)
def window(k):
    cx, cy, w = cam[k]; h = w * 16 / 9
    x0 = np.clip(cx - w / 2, 0, 2160 - w); y0 = np.clip(cy - 0.50 * h, 0, 3840 - h)
    return x0, y0, w, h
def crop(img, win):
    x0, y0, w, h = win; s = W / w
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
def to_out(win, x, y):
    x0, y0, w, h = win; s = W / w; return (x - x0) * s, (y - y0) * s

# ---------- overlays
def png(name):
    im = cv2.imread(f'{OV}/{name}.png', cv2.IMREAD_UNCHANGED); return im
_ov = {}
def ov(name):
    if name not in _ov: _ov[name] = png(name)
    return _ov[name]
def paste(base, im, x, y, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    if scale != 1.0:
        im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = im.shape[:2]; x = int(round(x)); y = int(round(y))
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    o = im[Y0 - y:Y1 - y, X0 - x:X1 - x].astype(np.float32); a = o[..., 3:4] / 255 * alpha
    base[Y0:Y1, X0:X1] = base[Y0:Y1, X0:X1] * (1 - a) + o[..., :3] * a
def ramp(t, t0, t1, fin=0.18, fout=0.18):
    if t < t0 or t > t1: return 0.0
    return min(1.0, (t - t0) / fin if fin else 1, (t1 - t) / fout if fout else 1)
def pop(t, t0, d=0.22):
    u = min(max((t - t0) / d, 0), 1); return d4.ease_out_back(u) if u < 1 else 1.0

SUB_Y = 1330                     # fixed top of every subtitle PNG (text centre ~ y 1378)
BOX = json.load(open(OV + '/boxes.json'))

def render(k):
    t = k / FPS; p, s = src_pos(t); win = window(k)
    a = int(math.floor(p)); u = p - a
    A = crop(frame(a), win)
    if s.get('ni'): A = crop(frame(int(round(p))), win)
    if u > 0.03 and a < 191 and not s.get('ni'):
        B = crop(frame(a + 1), win)
        f01, f10 = flows(A, B, 0.5); img = interp(A.astype(np.float32), B.astype(np.float32), f01, f10, u)
    else:
        img = A.astype(np.float32)
    # grade (natural daylight; the raw clip is blue/magenta)
    rgb = img[..., ::-1] / 255.0
    g = d4.grade(rgb).astype(np.float32)
    lab = cv2.cvtColor(g, cv2.COLOR_RGB2Lab); lab[..., 1] -= TL.get('a_shift', 4.0); lab[..., 2] += TL.get('b_shift', 2.0)
    lab[..., 0] = np.clip(lab[..., 0] * 1.03 + 1.5, 0, 100)
    g = np.clip(cv2.cvtColor(lab, cv2.COLOR_Lab2RGB), 0, 1)
    img = (g[..., ::-1] * 255).astype(np.float32)
    # freeze punch: tiny flash and subtle zoom handled by the camera; flash here
    for fz in TL.get('flash', []):
        if fz <= t < fz + 0.12: img = img + (255 - img) * 0.22 * (1 - (t - fz) / 0.12)
    fi = int(round(p))
    # ---- badges over heads
    for who, tr, seen, key in (('1', BL, black_seen, 'b1'), ('2', PK, pink_seen, 'b2')):
        ev = TL['badges'][key]
        if not (ev['on'] <= t <= ev['off']): continue
        if not seen[max(0, fi - 3):fi + 4].any() or t >= TL['end_on']: continue
        if any(h0 <= t <= h1 for h0, h1 in ev.get('hide', [])): continue
        ff = int(min(max(fi, ev.get('fmin', 0)), ev.get('fmax', 191)))
        bx, by = to_out(win, tr[0][ff], tr[2][ff])
        name = 'badge' + who + ('x' if t >= ev.get('x', 99) else '')
        al = ramp(t, ev['on'], ev['off'], 0.01, 0.25)
        paste(img, ov(name), max(bx - 56, 70), by - 150, al, pop(t, ev['on']))
    # ---- knee chip next to rider 1
    for c0, c1 in TL['chip']:
        if not (c0 <= t <= c1 and fi <= 58): continue
        ang = int(np.clip(round(BLK[fi] / 2) * 2, 80, 180))
        bx, by = to_out(win, BL[0][fi], BL[1][fi] + BL[3][fi] / 2)
        cxp = np.clip(bx - 180, 70, 850 - 360)
        paste(img, ov(f'chip{ang}'), cxp, min(by + 24, 1210), ramp(t, c0, c1, 0.15, 0.2))
    # ---- top: wordmark + hook title
    paste(img, ov('mark'), 0, 232, ramp(t, -1, TL['mark_off'], 0, 0.25))
    paste(img, ov('hook'), 0, 290, ramp(t, -1, TL['hook_off'], 0, 0.2))
    # ---- subtitles, one fixed position
    for name, t0, t1 in TL['subs']:
        al = ramp(t, t0, t1, 0.06, 0.08)
        if al > 0: paste(img, ov('sub_' + name), 0, SUB_Y, al)
    # ---- end card
    e0 = TL['end_on']
    if t >= e0:
        al = min(1, (t - e0) / 0.25); yy = np.arange(H, dtype=np.float32)[:, None, None]
        m = (0.22 + 0.45 * np.exp(-((yy - 700) / 330) ** 2)) * al
        img = img * (1 - m) + np.array([42, 36, 45], np.float32) * m
        ao = al * min(1, max(0, (TL['end_off'] + 0.2 - t) / 0.2))
        paste(img, ov('end'), 0, 520 + 30 * (1 - d4.ease_out_expo(min(1, (t - e0) / 0.4))), ao)
    # ---- loop tail: crossfade into frame 0 (blurred dissolve, no double exposure of riders)
    lt = TL['loop']
    if t > T_TOTAL - lt:
        v = (t - (T_TOTAL - lt)) / lt
        f0 = render.first
        bl = cv2.GaussianBlur(img, (0, 0), 3 + 30 * v)
        img = bl * (1 - v) + f0 * v
    return np.clip(img, 0, 255).astype(np.uint8)

render.first = None
if __name__ == '__main__':
    render.first = render(0).astype(np.float32)
    if ONLY:
        for k in [int(x) for x in ONLY.split(',')]:
            cv2.imwrite(f'{D}/still_{k:03d}.jpg', render(k), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit()
    ff = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                   '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=sp.PIPE)
    for k in range(NOUT):
        ff.stdin.write(render(k).tobytes())
        if k % 30 == 0: print('frame', k, '/', NOUT, flush=True)
    ff.stdin.close(); ff.wait(); print('done', OUT, NOUT / FPS)
