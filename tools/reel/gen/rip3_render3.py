"""rip v3 r8: murky/sandy plume close-up with tracked ring (st_rip1 5.0-7.0 s), plain float shot."""
import sys, subprocess as sp
import cv2, numpy as np
sys.argv=['x','/tmp/media/out/ci/rip3/gen','','/tmp/rr/out']
exec(open('/tmp/rr/render.py').read().split('# 1. hook')[0])
fr, pos = track(f'{G}/st_rip1.mp4', 0.0, int(7.0 * FPS), (320, 790))
w = writer(f'{O}/h_murky.mp4')
for i in range(int(4.2 * FPS), int(5.8 * FPS)):
    f = fr[i]; x, y = pos[i]; t = (i - 4.2 * FPS) / FPS; img = f.copy(); ring(img, (x, y), (165, 155), (t - 0.15) / 0.4)
    img = zoom(img, x, y - 40, 1.25); w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()
exec(open('/tmp/rr/render2.py').read().split('# foam heading out')[0].replace("G, O = sys.argv[1:3]", "G, O = '/tmp/media/out/ci/rip3/gen', '/tmp/rr/out'"))
w = writer(f'{O}/h_float.mp4')
for j, f in enumerate(frames(f'{G}/r3_float.mp4')):
    w.stdin.write(fit(f).tobytes())
w.stdin.close(); w.wait()
print('ok')
