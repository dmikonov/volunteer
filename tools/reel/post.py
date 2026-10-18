"""sheet + preview + HF upload. usage: python3 post.py <workdir>"""
import json, sys, subprocess as sp, cv2, numpy as np
from huggingface_hub import HfApi
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); f = f"{W}/{S['out']}"; nm = S['out'][:-4]
cap = cv2.VideoCapture(f); fps = cap.get(5); n = int(cap.get(7)); tiles = []; t = 0.0
while t < n / fps - 0.05:
    cap.set(1, int(t * fps)); ok, fr = cap.read()
    if not ok: break
    fr = cv2.resize(fr, (135, 240)); cv2.putText(fr, f'{t:.1f}', (3, 234), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1); tiles.append(fr); t += 0.3
while len(tiles) % 16: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(f'{W}/sheet.jpg', np.vstack([np.hstack(tiles[i:i + 16]) for i in range(0, len(tiles), 16)]), [cv2.IMWRITE_JPEG_QUALITY, 80])
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-maxrate', '3500k', '-bufsize', '7000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', f'{W}/prev.mp4'], check=True)
sp.run(f'base64 -w0 {W}/prev.mp4 > {W}/prev.b64', shell=True, check=True)
a = HfApi()
a.upload_file(path_or_fileobj=f, path_in_repo=f'tips/{nm}.mp4', repo_id='dmikonov/surftribe-drafts', repo_type='dataset')
a.upload_file(path_or_fileobj=f'{W}/sheet.jpg', path_in_repo=f'review/{nm}_sheet.jpg', repo_id='dmikonov/surftribe-gen-inputs', repo_type='dataset')
print('posted', nm)
