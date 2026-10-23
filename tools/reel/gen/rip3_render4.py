"""rip v3 r11: end recap on the real rip: tracked ring, coral arrow out with the current, cyan arrow parallel to the shore."""
import sys
sys.argv=['x','/tmp/media/out/ci/rip3/gen','','/tmp/rr/out']
exec(open('/tmp/rr/render.py').read().split('# 1. hook')[0])
fr, pos = track(f'{G}/st_rip1.mp4', 0.0, int(3.6 * FPS), (320, 790))
w = writer(f'{O}/h_recap.mp4')
for i in range(int(0.4 * FPS), int(3.6 * FPS)):
    t = (i - 0.4 * FPS) / FPS; x, y = pos[i]; img = fr[i].copy()
    ring(img, (x, y), (195, 175), 1.0)
    arrow(img, (x, y + 60), (x - 10, y - 240), t / 0.4, CO)
    arrow(img, (x - 10, y - 240), (x + 400, y - 90), (t - 0.45) / 0.5, CY)
    img = zoom(img, x + 150, y - 150, 1.05)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait(); print('ok')
