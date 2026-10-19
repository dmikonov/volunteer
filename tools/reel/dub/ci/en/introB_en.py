# EN variant B: same reel as r31v11 (Demc-jyDzi6), new 2.9 s intro that calls out beginners.
# Audio = original from 1.733 s (drops "Nobody tells beginners this"), video = new intro (88 frames) + original from frame 140.
import subprocess as sp, urllib.request, os, json
R = 'reels/r31/r31v11_en_trial.mp4'; D = 'tools/reel/dub/ci/en/'; O = 'out'; T = '/tmp/enb'
os.makedirs(T, exist_ok=True); os.makedirs(O, exist_ok=True)
SRC = {'white': 'https://cdn.coverr.co/videos/coverr-surfer-catching-a-wave-5342/1080p.mp4',
       'walk': 'https://assets.mixkit.co/videos/1032/1032-1080.mp4'}
for k, u in SRC.items():
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    open(f'{T}/{k}.mp4', 'wb').write(urllib.request.urlopen(req, timeout=120).read())
FPS = 30; OFF = 52; CUT = 140; NA = 38; NB = CUT - OFF - NA
def shot(i, ss, fx, nf, ov):
    crop = f"crop=w='min(iw,ih*9/16)':h=ih:x='(iw-min(iw,ih*9/16))*{fx}':y=0"
    return (f"[{i}:v]{crop},scale=1080:1920:flags=lanczos,fps={FPS},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1,"
            f"trim=end_frame={nf},setsar=1[s{i}];[s{i}][{ov}:v]overlay=0:0:eof_action=repeat,format=yuv420p[v{i}]")
# original ends with a 9-frame loop-back to its old hook (frames 795-803): replace with the new opening frames
END = 795; TAIL = 804 - END
fc = ';'.join([shot(0, 9.2, 0.51, NA, 3), "[v0]split[v0a][v0c]", f"[v0c]trim=end_frame={TAIL},setpts=PTS-STARTPTS[v0t]",
               shot(1, 15.2, 0.51, NB, 4),
               f"[2:v]fps={FPS},trim=start_frame={CUT}:end_frame={END},setpts=PTS-STARTPTS,setsar=1,format=yuv420p[v2]",
               "[v0a][v1][v2][v0t]concat=n=4:v=1:a=0[v]",
               f"[2:a]atrim=start={OFF / FPS:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02[a]"])
out = f'{O}/reel_beginners5_en_B.mp4'
sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', '9.2', '-i', f'{T}/white.mp4', '-ss', '15.2', '-i', f'{T}/walk.mp4', '-i', R,
        '-i', D + 'ovA.png', '-i', D + 'ovB.png', '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-r', str(FPS), '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', out], check=True)
pr = lambda *a: sp.run(a, capture_output=True, text=True)
log = [pr('ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,nb_frames,duration', '-of', 'compact', out).stdout,
       pr('ffmpeg', '-hide_banner', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-').stderr[-700:]]
open(f'{O}/beginners5_en_B_log.txt', 'w').write('\n'.join(log))
ts = [0.05, 1.2, 1.3, 2.9, 2.95, 23.0, 24.7, 24.75, 24.9, 25.03]
for i, t in enumerate(ts):
    sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', out, '-frames:v', '1', '-vf', f"scale=270:480,drawtext=text='{t}':x=8:y=8:fontsize=26:fontcolor=yellow:box=1:boxcolor=black", f'{T}/f{i:02d}.png'], check=True)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{T}/f%02d.png', '-vf', 'tile=5x2', '-frames:v', '1', f'{O}/beginners5_en_B_sheet.jpg'], check=True)
print('\n'.join(log))
