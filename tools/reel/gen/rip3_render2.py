"""rip v3 r6: more overlays on footage. foam arrow (real plume), current arrow on the float shot, parallel arrow on the paddle shot.
usage: python3 render2.py <gen_dir> <out_dir>"""
import sys, subprocess as sp, math
import cv2, numpy as np
G, O = sys.argv[1:3]
FPS = 25; W, H = 1080, 1920
CY = (255, 228, 0); CO = (80, 81, 255); SH = (42, 36, 45)

def writer(fn):
    return sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                     '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', fn], stdin=sp.PIPE)

def frames(fn, t0=0.0, dur=None):
    cap = cv2.VideoCapture(fn); fps = cap.get(5); n = int(cap.get(7)); out = []
    i0 = int(t0 * fps); i1 = n if dur is None else min(n, i0 + int(dur * fps))
    cap.set(1, i0)
    for i in range(i0, i1):
        ok, f = cap.read()
        if not ok: break
        out.append(f)
    if abs(fps - FPS) > 0.5:  # resample to 25 fps by nearest frame
        m = int(len(out) / fps * FPS); out = [out[min(len(out) - 1, int(k * fps / FPS))] for k in range(m)]
    return out

def arrow(img, p0, p1, prog, col):
    if prog <= 0: return
    prog = min(1, prog); p1 = (p0[0] + (p1[0] - p0[0]) * prog, p0[1] + (p1[1] - p0[1]) * prog)
    a = (int(p0[0]), int(p0[1])); b = (int(p1[0]), int(p1[1]))
    L = math.hypot(b[0] - a[0], b[1] - a[1]); tip = min(0.35, 70 / max(L, 1))
    cv2.arrowedLine(img, a, b, SH, 26, cv2.LINE_AA, tipLength=tip)
    cv2.arrowedLine(img, a, b, col, 14, cv2.LINE_AA, tipLength=tip)

def fit(f):  # small generated clip -> 1080x1920, lanczos + light unsharp (pipeline rule for 480x832)
    h, w = f.shape[:2]; s = H / h; f = cv2.resize(f, (int(round(w * s)), H), interpolation=cv2.INTER_LANCZOS4)
    x0 = (f.shape[1] - W) // 2; f = f[:, x0:x0 + W]
    bl = cv2.GaussianBlur(f, (0, 0), 1.2); return cv2.addWeighted(f, 1.35, bl, -0.35, 0)

def zoom(img, cx, cy, z):
    w, h = W / z, H / z; x0 = min(max(cx * W - w / 2, 0), W - w); y0 = min(max(cy * H - h / 2, 0), H - h)
    return cv2.warpAffine(img, np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]]), (W, H), flags=cv2.INTER_LANCZOS4)

# foam heading out: st_rip2 3.4-5.6 s, zoom 1.4 on the plume, coral arrow along it
w = writer(f'{O}/h_foam.mp4')
for j, f in enumerate(frames(f'{G}/st_rip2.mp4', 3.4, 2.2)):
    t = j / FPS; img = zoom(f, 0.3, 0.27, 1.4); arrow(img, (350, 1330), (320, 640), (t - 0.2) / 0.6, CO)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()

# caught: float shot, coral arrow = the current pulling away from the beach (beach is at the top of this shot)
w = writer(f'{O}/h_float.mp4')
for j, f in enumerate(frames(f'{G}/r3_float.mp4')):
    t = j / FPS; img = fit(f); arrow(img, (820, 1180), (820, 1560), (t - 0.3) / 0.6, CO)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()

# paddle parallel: paddle2 0-2.2 s, cyan arrow in his direction, along the beach line at the top
w = writer(f'{O}/h_paddle.mp4')
for j, f in enumerate(frames(f'{G}/r3_paddle2.mp4', 0, 2.2)):
    t = j / FPS; img = fit(f); arrow(img, (560, 760), (960, 760), (t - 0.1) / 0.6, CY)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()
print('ok')
