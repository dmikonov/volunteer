# contact sheets of stock clips to pick a new intro shot (not used in the original EN reel)
import subprocess as sp, urllib.request, os
T = '/tmp/cand'; O = 'out/cand'; os.makedirs(T, exist_ok=True); os.makedirs(O, exist_ok=True)
SRC = {'1127': 'https://assets.mixkit.co/videos/1127/1127-1080.mp4',
       'man': 'https://cdn.coverr.co/videos/coverr-guy-surfing-in-the-sea-9468/1080p.mp4',
       'white': 'https://cdn.coverr.co/videos/coverr-surfer-catching-a-wave-5342/1080p.mp4'}
info = []
for k, u in SRC.items():
    f = f'{T}/{k}.mp4'
    open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read())
    pr = sp.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=width,height,r_frame_rate:format=duration', '-of', 'compact', f], capture_output=True, text=True).stdout
    info.append(k + ' ' + pr.replace('\n', ' '))
    d = float(pr.split('duration=')[1].split()[0])
    n = 12; step = d / n
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-vf', f"fps=1/{step:.3f},crop=w='ih*9/16':h=ih:x='(iw-ih*9/16)*0.5',scale=216:384,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1,tile=12x1", '-frames:v', '1', f'{O}/{k}.jpg'], check=True)
open(f'{O}/info.txt', 'w').write('\n'.join(info))
