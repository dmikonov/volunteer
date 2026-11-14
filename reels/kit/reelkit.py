"""SurfTribe reel kit: EDL (JSON) -> 1080x1920 30 fps reel.
Built after reel 25 so Saturday footage turns into a reel the same day.

EDL format (all times in seconds of OUTPUT unless noted):
{
 "out": "path.mp4",
 "shots": [ {"src": "clip.mp4", "in": 3.2, "out": 5.0, "speed": 1.0,      # in/out in SOURCE seconds
             "rotate": 0|90|-90, "cx": 0.5, "cy": 0.5, "zoom": 1.0,        # crop centre (0..1 of source) and zoom (1 = full height)
             "zoom_to": 1.0, "freeze_at": null, "freeze_dur": 0,          # optional push-in and freeze on a source time
             "ring": {"x": 0.52, "y": 0.61, "r": 120, "t0": 0.2}}  ],     # ring on the freeze, x/y in OUTPUT fraction
 "cards": [ {"html": "<div ...>", "t0": 0.0, "t1": 1.8, "y": 300} ],         # any Chromium-rendered overlay (Hebrew RTL safe)
 "subs":  [ {"text": "...", "t0": 1.9, "t1": 3.4} ],                         # one fixed position, centred
 "end":   {"t0": 15.0, "html": "..."},
 "loop": 0.3, "grade": true
}
Rules baked in: subtitles at one fixed y (pill top 1330), centred at 540; no interpolation (real frames only,
speed < 1 repeats frames: keep slow-mo to clips shot at 50p and speed >= 0.5); loop dissolves only the picture."""
import sys, json, os, subprocess as sp, math, hashlib
import numpy as np, cv2
sys.path.insert(0, '/home/claude/work/prod/design'); sys.path.insert(0, '/home/claude/work/series')
import design4 as d4
from base import RUB, CYAN, CORAL, FOAM, PLUM
from playwright.sync_api import sync_playwright

W, H, FPS = 1080, 1920, 30
SUB_Y = 1330
FF = f"@font-face{{font-family:Rubik;src:url(data:font/ttf;base64,{RUB});font-weight:300 900}}"

def render_pngs(items, cache):
    """items: {name: (html, w, h)} -> transparent PNGs via Chromium, cached by content hash."""
    os.makedirs(cache, exist_ok=True); todo = {}
    paths = {}
    for k, (html, w, h) in items.items():
        hsh = hashlib.md5((html + str(w) + str(h)).encode()).hexdigest()[:12]; p = f'{cache}/{hsh}.png'; paths[k] = p
        if not os.path.exists(p): todo[p] = (html, w, h)
    if todo:
        with sync_playwright() as pw:
            b = pw.chromium.launch(); pg = b.new_page()
            for p, (html, w, h) in todo.items():
                doc = f"<!doctype html><html><head><meta charset=utf-8><style>{FF}html,body{{margin:0;background:transparent;width:{w}px;height:{h}px;overflow:hidden}}*{{font-family:Rubik;color:{FOAM}}}</style></head><body>{html}</body></html>"
                pg.set_viewport_size({'width': w, 'height': h}); pg.set_content(doc); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(50)
                pg.screenshot(path=p, omit_background=True)
            b.close()
    return {k: cv2.imread(p, cv2.IMREAD_UNCHANGED) for k, p in paths.items()}

def sub_html(t):
    return f"<div style='position:absolute;left:0;right:0;top:6px;text-align:center'><span dir=rtl style='display:inline-block;padding:10px 30px 14px;border-radius:22px;background:rgba(45,36,42,.62);font-weight:800;font-size:66px;line-height:1.1'>{t}</span></div>"

def paste(base, im, x, y, alpha=1.0):
    if alpha <= 0.01: return
    h, w = im.shape[:2]; x = int(round(x)); y = int(round(y))
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if X1 <= X0 or Y1 <= Y0: return
    o = im[Y0 - y:Y1 - y, X0 - x:X1 - x].astype(np.float32); a = o[..., 3:4] / 255 * alpha
    base[Y0:Y1, X0:X1] = base[Y0:Y1, X0:X1] * (1 - a) + o[..., :3] * a

def ramp(t, t0, t1, fin=0.12, fout=0.12):
    if t < t0 or t > t1: return 0.0
    return min(1.0, (t - t0) / fin if fin else 1, (t1 - t) / fout if fout else 1)

class Src:
    def __init__(self, path, rotate=0):
        self.cap = cv2.VideoCapture(path); self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25; self.rot = rotate; self.i = -1; self.f = None
    def at(self, t):
        n = int(round(t * self.fps))
        if n != self.i:
            if n != self.i + 1: self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
            ok, f = self.cap.read()
            if ok:
                if self.rot == 90: f = cv2.rotate(f, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif self.rot == -90: f = cv2.rotate(f, cv2.ROTATE_90_CLOCKWISE)
                self.f = f
            self.i = n
        return self.f

def crop916(img, cx, cy, zoom):
    h, w = img.shape[:2]; ch = h / zoom; cw = ch * 9 / 16
    if cw > w: cw = w; ch = cw * 16 / 9
    x0 = np.clip(cx * w - cw / 2, 0, w - cw); y0 = np.clip(cy * h - ch / 2, 0, h - ch)
    s = W / cw; M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)

def grade(bgr):
    g = d4.grade(bgr[..., ::-1].astype(np.float32) / 255).astype(np.float32)
    return (np.clip(g, 0, 1)[..., ::-1] * 255).astype(np.float32)

def build(edl):
    cache = os.path.dirname(os.path.abspath(edl['out'])) + '/ovcache'
    shots = edl['shots']; t_acc = 0
    for s in shots:
        s['dur'] = (s['out'] - s['in']) / s.get('speed', 1.0) + s.get('freeze_dur', 0); s['t0'] = t_acc; t_acc += s['dur']
    T = t_acc; N = int(round(T * FPS))
    items = {f'card{i}': (c['html'], W, c.get('h', 400)) for i, c in enumerate(edl.get('cards', []))}
    items.update({f'sub{i}': (sub_html(s['text']), W, 110) for i, s in enumerate(edl.get('subs', []))})
    if edl.get('end'): items['end'] = (edl['end']['html'], W, edl['end'].get('h', 500))
    ring = f"<div style='position:absolute;left:10px;top:10px;width:220px;height:220px;border-radius:50%;border:8px solid {CYAN};box-sizing:border-box'></div>"
    items['ring'] = (ring, 240, 240)
    OV = render_pngs(items, cache)
    srcs = {}
    def frame_at(t):
        for s in shots:
            if s['t0'] <= t < s['t0'] + s['dur'] or s is shots[-1]:
                u = t - s['t0']; sp_ = s.get('speed', 1.0); fz = s.get('freeze_at'); fd = s.get('freeze_dur', 0)
                src_t = s['in'] + u * sp_
                if fz is not None:
                    pre = (fz - s['in']) / sp_
                    if u >= pre: src_t = fz if u < pre + fd else fz + (u - pre - fd) * sp_
                key = (s['src'], s.get('rotate', 0))
                if key not in srcs: srcs[key] = Src(s['src'], s.get('rotate', 0))
                f = srcs[key].at(min(src_t, s['out']))
                z0, z1 = s.get('zoom', 1.0), s.get('zoom_to', s.get('zoom', 1.0)); z = z0 + (z1 - z0) * min(1, u / max(s['dur'], 1e-3))
                img = crop916(f, s.get('cx', .5), s.get('cy', .5), z)
                img = grade(img) if edl.get('grade', True) else img.astype(np.float32)
                if fz is not None and s.get('ring'):
                    r = s['ring']; pre = (fz - s['in']) / sp_
                    if pre + r.get('t0', 0) <= u < pre + fd:
                        paste(img, OV['ring'], r['x'] * W - 120, r['y'] * H - 120, min(1, (u - pre - r.get('t0', 0)) / 0.12))
                return img, s
    first = None
    ff = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                   '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', edl['out']], stdin=sp.PIPE)
    for k in range(N):
        t = k / FPS; img, s = frame_at(t)
        for i, c in enumerate(edl.get('cards', [])):
            paste(img, OV[f'card{i}'], 0, c.get('y', 300), ramp(t, c['t0'], c['t1']))
        e = edl.get('end')
        endon = e and t >= e['t0']
        for i, sb in enumerate(edl.get('subs', [])):
            if not endon: paste(img, OV[f'sub{i}'], 0, SUB_Y, ramp(t, sb['t0'], sb['t1'], 0.06, 0.08))
        if endon:
            al = min(1, (t - e['t0']) / 0.25); yy = np.arange(H, dtype=np.float32)[:, None, None]
            m = (0.22 + 0.45 * np.exp(-((yy - 700) / 330) ** 2)) * al
            img = img * (1 - m) + np.array([42, 36, 45], np.float32) * m
            t_off = e.get('t1', T - edl.get('loop', 0.3) - 0.2)
            paste(img, OV['end'], 0, e.get('y', 520), al * min(1, max(0, (t_off + 0.2 - t) / 0.2)))
        if k == 0: first = img.copy()
        lt = edl.get('loop', 0.3)
        if lt and t > T - lt:
            v = (t - (T - lt)) / lt; img = cv2.GaussianBlur(img, (0, 0), 3 + 30 * v) * (1 - v) + first * v
        ff.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait(); print('done', edl['out'], round(T, 2), 's')

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])))
