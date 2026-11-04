"""Wetsuit reel v22. Run in /tmp/r4/v22 on the HF sandbox (raw clips in ../raw, music ../ride.mp3, fonts ../fonts).
Changes vs v21: table = carousel p02; value on screen by ~3 s; ~19 s; no delogo smear; no unsharp (it made the AI
footage look plastic), light film grain instead; hood beat regenerated (plain suit, both gloves); single hook text;
subtitles centred at y 1360 with degrees F; end card fades from blur to the sharp first frame so the loop is seamless."""
import subprocess as sp, json, re, os, numpy as np, soundfile as sf, imageio_ffmpeg
F = imageio_ffmpeg.get_ffmpeg_exe(); R = '/tmp/r4/v22'; os.chdir(R)
def run(*a): sp.run([F, '-loglevel', 'error', '-y', *a], check=True)
def enc(args, out): run(*args, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30', out)

GRAIN = 'noise=c0s=7:c0f=t+u'
GRADE = {'warm': 'eq=saturation=0.78:contrast=1.03:gamma=0.98,', 'spring': 'eq=saturation=0.88,'}
# ---------- normalise raw 480x832 16 fps clips: motion-interpolate to 30 fps, upscale without sharpening, grain
for n in ('chest', 'warm', 'spring', 'macro', 'wade', 'booties', 'hood3'):
    if os.path.exists(f'n_{n}.mp4'): continue
    run('-i', f'../raw/{n}.mp4', '-vf', f'{GRADE.get(n, "")}minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,'
        f'scale=1108:1920:flags=lanczos,crop=1080:1920,setsar=1', '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '15', '-pix_fmt', 'yuv420p', f'n_{n}.mp4')

# ---------- voice: trim silence, keep word timings exact
W = json.load(open('words.json'))
N = len(W); vo, words = [], []
for i in range(N):
    a, sr = sf.read(f'vo_{i}.wav'); env = np.abs(a) > 10 ** (-42 / 20)
    s0 = max(0, np.argmax(env) - int(0.02 * sr)); s1 = min(len(a), len(a) - np.argmax(env[::-1]) + int(0.04 * sr))
    sf.write(f'vt_{i}.wav', a[s0:s1], sr); vo.append((s1 - s0) / sr)
    words.append([[t, max(0, st - s0 / sr), max(0, en - s0 / sr)] for t, st, en in W[str(i)]['words']])
d = [max(v + 0.25, 1.6) for v in vo]; d[0] = vo[0] + 0.3; d[-1] = vo[-1] + 0.6
st = [sum(d[:i]) for i in range(N)]; T = sum(d)
vstart = [s + (0.0 if i == 0 else 0.05) for i, s in enumerate(st)]

# ---------- beats: clip, start, slow factor, overlay, pre-filter
B = [('n_chest.mp4', 0.0, 1.0, 'h0', 'HOOK'),
     ('n_warm.mp4', 0.3, 1.0, 'r0', ''),
     ('n_spring.mp4', 0.0, 1.0, 'r1', 'crop=900:1600:90:0,scale=1080:1920,setsar=1,'),
     ('n_macro.mp4', 0.0, 1.0, 'r2', ''),
     ('n_wade.mp4', 0.0, 1.0, 'r3', ''),
     ('n_booties.mp4', 1.25, 2.3, 'r4', 'crop=844:1500:118:420,scale=1080:1920,setsar=1,'),  # clean source 1.25-2.23 s only
     ('n_hood3.mp4', 2.15, 1.75, 'r5', ''),  # big breath puffs before 2.1 s read as smoke, start after them
     ('n_chest.mp4', 0.0, 1.0, 'end', 'END')]
FADE = 'format=rgba,fade=t=in:st=0.03:d=0.15:alpha=1'
OVF = "overlay=x=0:y='if(lt(t,0.18),max(0,46*(0.18-t)/0.15),0)'"
REB = [int(x) for x in os.environ.get('REBUILD', ','.join(map(str, range(N)))).split(',')]
D0A = min(1.9, d[0] / 2 + 0.2)
for i, (clip, ss, k, ov, ex) in enumerate(B):
    if i not in REB and os.path.exists(f'b{i}.mp4'): continue
    ovin = ['-loop', '1', '-t', f'{d[i] + 0.5:.3f}', '-i', f'ov/{ov}.png']
    cap = f'[1:v]{FADE}[c];[v][c]{OVF},{GRAIN}' if i not in (0, N - 1) else f'[1:v]format=rgba[c];[v][c]overlay=0:0,{GRAIN}'
    if ex == 'HOOK':
        # wide, then a punch-in on the same clip (no shot longer than ~2 s); hook text is on screen at frame 0
        b0 = d[0] - D0A
        pre = (f'[0:v]split[p][q];[p]trim=0:{D0A:.3f},setpts=PTS-STARTPTS,setsar=1[x];'
               f'[q]trim=start={D0A - 0.45:.3f},setpts=PTS-STARTPTS,crop=760:1351:160:150,scale=1080:1920,setsar=1,'
               f'tpad=stop_mode=clone:stop_duration=3,trim=0:{b0:.3f},setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1:a=0[v]')
    elif ex == 'END':
        # the opening clip played backwards ends exactly on frame 0; blur fades out over the last 0.5 s
        D = d[i]
        kx = f'min(1,max(0,(T-{D - 0.5:.3f})/0.5))'
        pre = (f'[0:v]trim=0:{D:.3f},setpts=PTS-STARTPTS,reverse,format=yuv420p,split[s][b];'
               f'[b]boxblur=14:2,eq=brightness=-0.2:saturation=0.7[bb];'
               f"[bb][s]blend=all_expr='A*(1-{kx})+B*{kx}'[v]")
    else:
        pre = f'[0:v]{ex}trim=start={ss},setpts={k}*(PTS-STARTPTS),tpad=stop_mode=clone:stop_duration=1,trim=0:{d[i]:.3f},setpts=PTS-STARTPTS[v]'
    enc(['-i', clip, *ovin, '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
open('list.txt', 'w').write(''.join(f'file b{i}.mp4\n' for i in range(N)))
run('-f', 'concat', '-i', 'list.txt', '-c', 'copy', 'v.mp4')

# ---------- subtitles: fixed text per chunk (degrees F written out), timed from word stamps; line 0 is the hook headline itself
SUB = {1: ['75°F and up?', 'Boardshorts or a rash guard'], 2: ['65 to 75°F?', 'A spring suit'], 3: ['60 to 65°F?', 'A 3/2 full suit'],
       4: ['55 to 60°F?', 'A 4/3'], 5: ['48 to 55°F?', 'Add booties'], 6: ['Under 48°F?', 'A hooded 5/4'],
       7: ['Save this', 'SurfTribe, your AI surf coach']}
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h}:{m:02d}:{s:05.2f}'
ev = []
for i, chunks in SUB.items():
    w = words[i]
    q = next(j for j, x in enumerate(w) if x[0] in ('?', '.'))   # first question mark or full stop splits the line
    parts = [(w[0][1], w[q][2]), (w[q + 1][1] if q + 1 < len(w) else w[q][2], w[-1][2])]
    for (a0, a1), txt in zip(parts, chunks):
        ev.append([vstart[i] + a0, vstart[i] + a1 + 0.15, st[i] + d[i], txt])
lines = []
for j, (s0, s1, lim, txt) in enumerate(ev):
    nxt = ev[j + 1][0] if j + 1 < len(ev) else 1e9
    s1 = min(s1, lim, nxt - 0.02)
    lines.append(f"Dialogue: 0,{ts(s0)},{ts(s1)},Sub,,0,0,0,,{{\\an8\\pos(540,1360)\\fad(60,0)\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)}}{txt}")
ass = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
       "Style: Sub,Rubik ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H00201820,&H80000000,0,0,0,0,100,100,0,0,1,6,2,8,110,110,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + '\n'.join(lines) + '\n')
open('subs.ass', 'w').write(ass)
run('-i', 'v.mp4', '-vf', 'subtitles=subs.ass:fontsdir=/tmp/r4/fonts', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', 'vs.mp4')

# ---------- music window by RMS, quiet constant bed, two-pass loudnorm
raw = sp.run([F, '-loglevel', 'error', '-i', '../ride.mp3', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.int16).astype(float); hop = 4000
rms = np.array([np.sqrt(np.mean(m[k:k + hop] ** 2)) for k in range(0, len(m) - hop, hop)])
win = int(np.ceil(T * 2)); best = int(np.argmax([rms[k:k + win].mean() for k in range(0, len(rms) - win)])) / 2
ins, fc = [], ''
for i in range(N):
    ins += ['-i', f'vt_{i}.wav']; ms = int(vstart[i] * 1000); fc += f'[{i + 2}:a]aresample=48000,adelay={ms}|{ms}[v{i}];'
fc += ''.join(f'[v{i}]' for i in range(N)) + f'amix=inputs={N}:normalize=0,aformat=channel_layouts=stereo[vo];'
fc += f'[1:a]atrim={best:.2f}:{best + T:.2f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.019,afade=t=in:d=0.15,afade=t=out:st={T - 0.6:.2f}:d=0.6[m];[vo][m]amix=inputs=2:normalize=0,apad,atrim=0:{T:.3f}[a]'
run('-i', 'vs.mp4', '-i', '../ride.mp3', *ins, '-filter_complex', fc, '-map', '[a]', '-c:a', 'pcm_s16le', 'mix.wav')
meas = sp.run([F, '-hide_banner', '-i', 'mix.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
J = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}:"
      f"measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true,aresample=48000")
run('-i', 'vs.mp4', '-i', 'mix.wav', '-filter_complex', f'[1:a]{ln}[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'wetsuit_v22.mp4')
info = {'T': round(T, 3), 'd': [round(float(x), 3) for x in d], 'st': [round(float(x), 3) for x in st], 'music_start': float(best), 'subs': len(lines),
        'vstart': [round(float(x), 3) for x in vstart], 'vo': [round(float(x), 3) for x in vo]}
json.dump(info, open('info.json', 'w')); print('BUILD_OK', info)
