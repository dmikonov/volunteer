"""20.10 look2: remove the floating leash plug behind the tail in g_down (rule 17) by inpainting dark pixels in a small box.
usage: python3 deplug.py in.mp4 out.mp4"""
import sys, cv2, numpy as np, subprocess as sp
src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); fr = []
while True:
    ok, f = cap.read()
    if not ok: break
    fr.append(f)
H, W = fr[0].shape[:2]
p = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', out], stdin=sp.PIPE)
for i, f in enumerate(fr):
    t = i / fps
    if t < 2.05:
        x0, x1, y0, y1 = (286, 350, 560, 635) if t < 1.55 else (280, 345, 578, 635)
        g = cv2.cvtColor(f[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
        m = np.zeros((H, W), np.uint8); m[y0:y1, x0:x1] = (g < 90).astype(np.uint8) * 255
        m = cv2.dilate(m, np.ones((7, 7), np.uint8))
        if m.any(): f = cv2.inpaint(f, m, 5, cv2.INPAINT_TELEA)
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait()
