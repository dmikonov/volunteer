"""Wetsuit reel v22. Table = carousel p02. Hook gets the first value on screen by ~3 s, 8 beats, ~19 s.
Clips: only the ones that passed the full-res audit (chest, warm, spring first 2 s, macro, wade, booties 1.25-2.1 s,
bstand first 0.95 s, hood5 first 2 s). No delogo patches. Run in /tmp/r22 on the HF sandbox."""
import subprocess as sp, json, re, os, numpy as np, soundfile as sf, imageio_ffmpeg
F = imageio_ffmpeg.get_ffmpeg_exe(); R = '/tmp/r22'; C = '/tmp/r4'; os.chdir(R)
def run(*a): sp.run([F, '-loglevel', 'error', '-y', *a], check=True)
def enc(args, out): run(*args, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30', out)

# ---------- voice: trim silence, keep word timings exact
W = json.load(open('words.json')); N = len(W)
vo, words = [], []
for i in range(N):
    a, sr = sf.read(f'vo_{i}.wav'); env = np.abs(a) > 10 ** (-42 / 20)
    s0 = max(0, np.argmax(env) - int(0.02 * sr)); s1 = min(len(a), len(a) - np.argmax(env[::-1]) + int(0.04 * sr))
    sf.write(f'vt_{i}.wav', a[s0:s1], sr); vo.append((s1 - s0) / sr)
    words.append([[t, max(0, st - s0 / sr), max(0, en - s0 / sr)] for t, st, en in W[str(i)]['words']])
d = [max(v + 0.28, 1.6) for v in vo]; d[-1] = vo[-1] + 0.55
st = [sum(d[:i]) for i in range(N)]; T = sum(d)
vstart = [s + (0.0 if i == 0 else 0.05) for i, s in enumerate(st)]

FADE = 'format=rgba,fade=t=in:st=0.03:d=0.15:alpha=1'
OVF = "overlay=x=0:y='if(lt(t,0.18),max(0,46*(0.18-t)/0.15),0)'"
NORM = 'scale=1080:1920,setsar=1,'
B = ['n_chest3.mp4', 'n_warm.mp4', 'n_spring.mp4', 'MACRO_A', 'MACRO_B', 'BOOTIES', 'n_hood6.mp4', 'LOOP']
HOOK = 'n_chest3.mp4'  # regenerated from frame 0 of chest with the chest badge inpainted; arms stay crossed
OV = ['h0', 'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'end']
REB = [int(x) for x in os.environ.get('REBUILD', ','.join(map(str, range(N)))).split(',')]
for i in range(N):
    if i not in REB and os.path.exists(f'b{i}.mp4'): continue
    ovin = ['-loop', '1', '-t', f'{d[i] + 0.5:.3f}', '-i', f'ov/{OV[i]}.png']
    cap = '[1:v]format=rgba[c];[v][c]overlay=0:0' if i == 0 else f'[1:v]{FADE}[c];[v][c]{OVF}'
    if i == 0:
        # wide shot, then a punch-in of the same clip (no shot over 2.5 s); hook text up at frame 0
        a = min(2.0, d[0] / 2 + 0.2); b = d[0] - a
        pre = (f'[0:v]split[p][q];[p]trim=0:{a:.3f},setpts=PTS-STARTPTS,setsar=1[x];'
               f'[q]trim=start={a - 0.45:.3f},setpts=PTS-STARTPTS,crop=760:1351:160:150,{NORM}tpad=stop_mode=clone:stop_duration=3,trim=0:{b:.3f},setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1:a=0[v]')
        enc(['-i', f'{C}/{HOOK}', *ovin, '-filter_complex', f'{pre};{cap}', '-t', f'{d[0]:.3f}'], f'b{i}.mp4')
    elif B[i] == 'BOOTIES':
        # A: walk, n_booties 1.25-2.10 s slowed (clean span); B: standing split-toe booties, first 0.95 s
        a = round(d[i] * 0.55, 3); b = d[i] - a; k = a / 0.85
        pre = (f'[0:v]crop=844:1500:118:420,{NORM}trim=start=1.25,setpts={k:.3f}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc,trim=0:{a:.3f},setpts=PTS-STARTPTS,format=yuv420p[sa];'
               f'[2:v]crop=760:1351:160:569,{NORM}trim=0:0.95,setpts={b / 0.95:.3f}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=blend,tpad=stop_mode=clone:stop_duration=1,trim=0:{b:.3f},setpts=PTS-STARTPTS,format=yuv420p[sb];'
               f'[sa][sb]concat=n=2:v=1:a=0[v]')
        enc(['-i', f'{C}/n_booties.mp4', *ovin, '-i', f'{C}/n_bstand.mp4', '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
    elif B[i] in ('MACRO_A', 'MACRO_B'):
        # the wade clip has foam artifacts at every speed, so rows 3 and 4 share the clean, nearly static macro back:
        # wide for 3/2 (source 0-1.75 s), punch-in for 4/3 (source 1.75-3.5 s). Low motion, so the slow-down stays clean
        s0, crop = (0.0, '') if B[i] == 'MACRO_A' else (1.75, 'crop=830:1476:125:120,' + NORM)
        k = d[i] / 1.75
        pre = (f'[0:v]trim=start={s0},setpts=PTS-STARTPTS,{crop}setpts={k:.3f}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc,'
               f'tpad=stop_mode=clone:stop_duration=1,trim=0:{d[i]:.3f},setpts=PTS-STARTPTS[v]')
        enc(['-i', f'{C}/n_macro.mp4', *ovin, '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
    elif B[i] == 'LOOP':
        # recap over the opening clip played backwards: blurred while the card is up, sharp for the last 0.35 s,
        # so the reel ends exactly on frame 0 of the hook (seamless loop)
        e = d[i] - 0.3
        pre = (f"[0:v]trim=0:{d[i]:.3f},setpts=PTS-STARTPTS,reverse,format=yuv420p,split[s][q];"
               f"[q]boxblur=34:3,eq=brightness=-0.3:saturation=0.6,format=rgba,fade=t=out:st={e:.3f}:d=0.3:alpha=1[bl];[s][bl]overlay=0:0,format=yuv420p[v]")
        capl = f"[1:v]{FADE},fade=t=out:st={e - 0.35:.3f}:d=0.3:alpha=1[c];[v][c]{OVF}"
        enc(['-i', f'{C}/{HOOK}', *ovin, '-filter_complex', f'{pre};{capl}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
    else:
        ex = {'n_spring.mp4': 'crop=900:1600:90:0,' + NORM, 'n_warm.mp4': 'eq=saturation=0.82,'}.get(B[i], '')
        k = 1.0
        if B[i] == 'n_spring.mp4': k = max(1.0, d[i] / 2.0)  # foam turns to a mesh after ~2 s
        if B[i] == 'n_wade.mp4': k = max(1.0, d[i] / 1.35)   # a loose dark lump appears in the foam from ~1.4 s
        mi = ',minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc' if k > 1.01 else ''
        pre = f'[0:v]{ex}setpts={k:.3f}*(PTS-STARTPTS){mi},tpad=stop_mode=clone:stop_duration=3,trim=0:{d[i]:.3f},setpts=PTS-STARTPTS[v]'
        enc(['-i', f'{C}/{B[i]}', *ovin, '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
open('list.txt', 'w').write(''.join(f'file b{i}.mp4\n' for i in range(N)))
run('-f', 'concat', '-i', 'list.txt', '-c', 'copy', 'v.mp4')

# ---------- subtitles: none on beat 0 (the headline is the spoken line), then phrase chunks with units shown
DISP = {1: ['75°F and up?', 'Boardshorts'], 2: ['65 to 75°F?', 'A spring suit'], 3: ['60 to 65°F?', 'A 3/2'],
        4: ['55 to 60°F?', 'A 4/3'], 5: ['48 to 55°F?', 'Add booties'], 6: ['Under 48°F?', '5/4, with a hood'],
        7: ['Save this', 'so you never freeze']}
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h}:{m:02d}:{s:05.2f}'
ev = []
for i in range(1, N):
    toks = []
    for t, a0, a1 in words[i]:
        if re.fullmatch(r"[^\w']+", t):
            if toks: toks[-1][0] += t.strip()
            continue
        if toks and toks[-1][0].endswith('-'): toks[-1][0] += t; toks[-1][2] = a1; continue
        toks.append([t, a0, a1])
    chunks, cur = [], []
    for w in toks:
        cur.append(w)
        if w[0].endswith('?') or (i == N - 1 and w[0].endswith(',')): chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    assert len(chunks) == len(DISP[i]), (i, [[w[0] for w in c] for c in chunks])
    for c, txt in zip(chunks, DISP[i]):
        ev.append([vstart[i] + c[0][1], vstart[i] + c[-1][2] + 0.15, st[i] + d[i], txt])
lines = []
for j, (s0, s1, lim, txt) in enumerate(ev):
    nxt = ev[j + 1][0] if j + 1 < len(ev) else 1e9
    s1 = min(s1, lim, nxt - 0.02)
    anim = '\\fad(60,0)\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)'
    lines.append(f"Dialogue: 0,{ts(s0)},{ts(s1)},Sub,,0,0,0,,{{\\an8\\pos(540,1360){anim}}}{txt}")
ass = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
       "Style: Sub,Rubik ExtraBold,66,&H00FFFFFF,&H00FFFFFF,&H00201820,&H80000000,0,0,0,0,100,100,0,0,1,6,2,8,110,110,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + '\n'.join(lines) + '\n')
open('subs.ass', 'w').write(ass)
run('-i', 'v.mp4', '-vf', f'subtitles=subs.ass:fontsdir={C}/fonts', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', 'vs.mp4')

# ---------- music window by RMS, quiet constant bed, voice on top, two-pass loudnorm
raw = sp.run([F, '-loglevel', 'error', '-i', f'{C}/ride.mp3', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.int16).astype(float); hop = 4000
rms = np.array([np.sqrt(np.mean(m[k:k + hop] ** 2)) for k in range(0, len(m) - hop, hop)])
win = int(np.ceil(T * 2)); best = int(np.argmax([rms[k:k + win].mean() for k in range(0, len(rms) - win)])) / 2
ins, fc = [], ''
for i in range(N):
    ins += ['-i', f'vt_{i}.wav']; ms = int(vstart[i] * 1000); fc += f'[{i + 2}:a]aresample=48000,adelay={ms}|{ms}[v{i}];'
fc += ''.join(f'[v{i}]' for i in range(N)) + f'amix=inputs={N}:normalize=0,aformat=channel_layouts=stereo[vo];'
fc += f'[1:a]atrim={best:.2f}:{best + T:.2f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.019,afade=t=in:d=0.15,afade=t=out:st={T - 0.6:.2f}:d=0.6[m];[vo][m]amix=inputs=2:normalize=0,apad,atrim=0:{T:.3f}[a]'
run('-i', 'vs.mp4', '-i', f'{C}/ride.mp3', *ins, '-filter_complex', fc, '-map', '[a]', '-c:a', 'pcm_s16le', 'mix.wav')
meas = sp.run([F, '-hide_banner', '-i', 'mix.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
J = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}:"
      f"measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true,aresample=48000")
OUTV = os.environ.get('OUTV', 'wetsuit_v22.mp4')
run('-i', 'vs.mp4', '-i', 'mix.wav', '-filter_complex', f'[1:a]{ln}[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUTV)
info = {'T': round(T, 3), 'd': [round(float(x), 3) for x in d], 'music_start': float(best), 'subs': len(lines),
        'vstart': [round(float(x), 3) for x in vstart], 'vo': [round(float(x), 3) for x in vo], 'out': OUTV}
json.dump(info, open('info.json', 'w'))
print('BUILD_OK', info)
