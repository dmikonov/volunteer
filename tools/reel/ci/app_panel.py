"""App screen as a large panel on a blurred background (20.10, foam reel).
Card goes above the panel (y 250-470), subtitles below it (y 1298): neither covers app text or buttons.
usage: python3 app_panel.py <src.mp4> <a0> <a1> <crop_y0> <crop_h> <btn_y0> <btn_y1> <total_sec> <out.mp4>"""
import sys, subprocess as sp, numpy as np, cv2
src, a0, a1, y0, h, b0, b1, T, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), float(sys.argv[8]), sys.argv[9]
X0 = int(sys.argv[10]) if len(sys.argv) > 10 else 0; CW = int(sys.argv[11]) if len(sys.argv) > 11 else 1080; PY0 = int(sys.argv[12]) if len(sys.argv) > 12 else 500
PW = 900; PX = 90; PY = PY0; ph = round(h * PW / CW / 2) * 2; s = PW / CW
m = np.zeros((ph, PW), np.uint8); r = 34
cv2.rectangle(m, (r, 0), (PW - r, ph), 255, -1); cv2.rectangle(m, (0, r), (PW, ph - r), 255, -1)
for cx, cy in ((r, r), (PW - r, r), (r, ph - r), (PW - r, ph - r)): cv2.circle(m, (cx, cy), r, 255, -1)
cv2.imwrite('/tmp/panel_mask.png', m)
by0 = PY + int((b0 - y0) * s) - 12; by1 = PY + int((b1 - y0) * s) + 12; d = a1 - a0
fc = (f"[0:v]trim={a0}:{a1},setpts=PTS-STARTPTS,fps=25,tpad=stop_mode=clone:stop_duration={T - d + 0.2},split[a][b];"
      f"[a]crop=1080:1920:0:214,boxblur=40:3,eq=brightness=-0.42:saturation=0.35[bg];"
      f"[b]crop={CW}:{h}:{X0}:{y0},scale={PW}:{ph}:flags=lanczos,format=rgba[fg0];[1:v]format=gray,scale={PW}:{ph}[mk];[fg0][mk]alphamerge[fg];"
      f"[bg][fg]overlay={PX}:{PY},trim=duration={T},format=yuv420p[v]")
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-loop', '1', '-i', '/tmp/panel_mask.png', '-filter_complex', fc, '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-t', str(T), out], check=True)
print('panel', out, 'button box y', by0, by1)
