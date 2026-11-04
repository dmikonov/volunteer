"""rip v3 r4: special clips rendered with overlays drawn on the footage (tracked ring, arrows, app card).
usage: python3 render.py <gen_dir> <app_dir> <out_dir>"""
import sys, json, subprocess as sp, math
import cv2, numpy as np
G, APP, O = sys.argv[1:4]
FPS = 25; W, H = 1080, 1920
CY = (255, 228, 0)      # #00E4FF in BGR
CO = (80, 81, 255)      # #FF5150 in BGR
SH = (42, 36, 45)       # plum shadow #2D242A

def writer(fn):
    return sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                     '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', fn], stdin=sp.PIPE)

def track(fn, t0, n, p0):
    cap = cv2.VideoCapture(fn); cap.set(1, int(t0 * FPS)); prev = None; x, y = p0; pos = []; frames = []
    for i in range(n):
        ok, f = cap.read()
        if not ok: f = frames[-1].copy()
        g = cv2.cvtColor(cv2.resize(f, (270, 480)), cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None:
            (dx, dy), _ = cv2.phaseCorrelate(prev, g); x += dx * 4; y += dy * 4
        prev = g; pos.append((x, y)); frames.append(f)
    return frames, pos

def ring(img, c, ax, prog, col=CY):
    if prog <= 0: return
    a = int(360 * min(1, prog)); c = (int(c[0]), int(c[1]))
    cv2.ellipse(img, c, ax, -90, 0, a, SH, 18, cv2.LINE_AA)
    cv2.ellipse(img, c, ax, -90, 0, a, col, 10, cv2.LINE_AA)

def arrow(img, p0, p1, prog, col):
    if prog <= 0: return
    prog = min(1, prog); p1 = (p0[0] + (p1[0] - p0[0]) * prog, p0[1] + (p1[1] - p0[1]) * prog)
    a = (int(p0[0]), int(p0[1])); b = (int(p1[0]), int(p1[1]))
    L = math.hypot(b[0] - a[0], b[1] - a[1]); tip = min(0.35, 70 / max(L, 1))
    cv2.arrowedLine(img, a, b, SH, 26, cv2.LINE_AA, tipLength=tip)
    cv2.arrowedLine(img, a, b, col, 14, cv2.LINE_AA, tipLength=tip)

def zoom(img, cx, cy, z):
    w, h = W / z, H / z; x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4)

# 1. hook: real rip plume, ring tracked on it from 0.3 s, gentle zoom, closer from 2.1 s
fr, pos = track(f'{G}/st_rip1.mp4', 0.0, int(4.8 * FPS), (320, 790))
w = writer(f'{O}/h_hook.mp4')
for i, (f, (x, y)) in enumerate(zip(fr, pos)):
    t = i / FPS; img = f.copy(); ring(img, (x, y), (195, 175), (t - 0.3) / 0.45)
    z = 1.12 + 0.04 * t / 2.1 if t < 2.1 else 1.42 + 0.06 * (t - 2.1) / 2.7
    img = zoom(img, x + 60, y - 60, z)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()

# 2. "drags you out": the same kind of plume at 2x speed, coral arrow out to sea along it
cap = cv2.VideoCapture(f'{G}/st_rip2.mp4'); n = int(cap.get(7)); frames = []
for i in range(n):
    ok, f = cap.read()
    if ok: frames.append(f)
w = writer(f'{O}/h_drag.mp4')
for j, f in enumerate(frames[::2]):
    t = j / FPS; img = f.copy(); arrow(img, (300, 900), (262, 560), (t - 0.25) / 0.6, CO)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()

# 3. escape: coral arrow out with the current, then cyan arrow sideways, parallel to the shore line
fr = frames[int(5.2 * FPS):int(5.2 * FPS) + int(2.0 * FPS)]
while len(fr) < int(2.0 * FPS): fr.append(fr[-1])
w = writer(f'{O}/h_escape.mp4')
for j, f in enumerate(fr):
    t = j / FPS; img = f.copy()
    arrow(img, (300, 840), (270, 470), t / 0.5, CO)
    arrow(img, (300, 470), (900, 640), (t - 0.6) / 0.7, CY)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()

# 4. app: the forecast screen's wave height card, big, on a blurred copy of the screen, slow push-in
for L, x0 in (('en', 86), ('he', 510)):
    cap = cv2.VideoCapture(f'{APP}/forecast_{L}_height.mp4'); afps = cap.get(5); cap.set(1, int(3.0 * afps)); fr = []
    for i in range(int(3.6 * afps)):
        ok, f = cap.read()
        if ok: fr.append(f)
    w = writer(f'{O}/app_{L}_card.mp4')
    for j in range(int(3.6 * FPS)):
        f = fr[min(len(fr) - 1, int(j / FPS * afps))]
        bg = cv2.GaussianBlur(f[209:209 + H, :], (0, 0), 28) * 0.62
        card = f[502:904, x0:x0 + 478]; s = 2.1 + 0.08 * j / (3.6 * FPS)
        c = cv2.resize(card, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
        img = bg.astype(np.uint8); ch, cw = c.shape[:2]; yy = 940 - ch // 2; xx = (W - cw) // 2
        img[max(yy, 0):yy + ch, max(xx, 0):xx + cw] = c[max(-yy, 0):, max(-xx, 0):][:H - max(yy, 0), :W - max(xx, 0)]
        w.stdin.write(img.tobytes())
    w.stdin.close(); w.wait()
print('ok')
