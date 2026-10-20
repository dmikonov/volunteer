"""Rule 39: end 0.6 s after the last word. usage: python3 trim_tail.py <workdir>"""
import json, sys, os, subprocess as sp
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); tl = json.load(open(f'{W}/tl.json')); f = f"{W}/{S['out']}"
end = round(tl['L'][-1]['words'][-1][2] + 0.5, 2)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-t', str(end), '-af', f'afade=t=out:st={end - 0.35}:d=0.35', '-threads', '1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f + '.t.mp4'], check=True)
os.replace(f + '.t.mp4', f); print('trimmed', f, end)
