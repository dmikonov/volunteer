"""sheet + preview, no HF upload (Composio sandbox, 19.10). usage: python3 post_cz.py <workdir>"""
import json, sys, subprocess as sp, cv2, numpy as np
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); f = f"{W}/{S['out']}"
cap = cv2.VideoCapture(f); fps = cap.get(5); n = int(cap.get(7)); tiles = []; t = 0.0
while t < n / fps - 0.05:
    cap.set(1, int(t * fps)); ok, fr = cap.read()
    if not ok: break
    fr = cv2.resize(fr, (135, 240)); cv2.putText(fr, f'{t:.1f}', (3, 234), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1); tiles.append(fr); t += 0.3
while len(tiles) % 16: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(f'{W}/sheet.jpg', np.vstack([np.hstack(tiles[i:i + 16]) for i in range(0, len(tiles), 16)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-threads', '1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-maxrate', '3500k', '-bufsize', '7000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', f'{W}/prev.mp4'], check=True)
print('post ok')
