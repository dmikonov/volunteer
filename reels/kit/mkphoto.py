import sys, subprocess as sp, numpy as np, cv2
src, out, g0, g1, z0, z1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
im = cv2.imread(src); h, w = im.shape[:2]
bg = cv2.resize(im, (1080, int(h * 1080 / w))); bg = cv2.GaussianBlur(bg, (0, 0), 28); bg = (bg * 0.55).astype(np.uint8)
N = 75; ff = sp.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '25', '-i', '-', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', out], stdin=sp.PIPE)
gc = (g0 + g1) / 2; s0 = 960 / (g1 - g0)          # garment (y g0..g1 in source px) fills 960 output px
canvas_bg = np.zeros((1920, 1080, 3), np.uint8); y = 1410 - bg.shape[0] // 2
canvas_bg[max(0, y):min(1920, y + bg.shape[0])] = bg[max(0, -y):max(0, -y) + min(1920, y + bg.shape[0]) - max(0, y)]
for k in range(N):
    s = s0 * (z0 + (z1 - z0) * k / (N - 1))
    M = np.float32([[s, 0, 540 - w / 2 * s], [0, s, 1410 - gc * s]])
    fg = cv2.warpAffine(im, M, (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    mask = cv2.warpAffine(np.full((h, w), 255, np.uint8), M, (1080, 1920))
    mask = cv2.GaussianBlur(mask, (0, 0), 6)[..., None] / 255.0
    fr = (fg * mask + canvas_bg * (1 - mask)).astype(np.uint8)
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()
