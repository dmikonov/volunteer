"""Wetsuit reel v10: af_heart voice, word-timed subtitles (ASS), RMS-chosen music window, two-pass loudnorm,
QA: loop SSIM-ish, face vs text overlap, frame sheet. Run in /tmp/r4 on the HF sandbox."""
import subprocess as sp, json, re, os, numpy as np, soundfile as sf, imageio_ffmpeg
F = imageio_ffmpeg.get_ffmpeg_exe(); R = '/tmp/r4'; os.chdir(R)
def run(*a): sp.run([F, '-loglevel', 'error', '-y', *a], check=True)
def enc(args, out): run(*args, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', '30', out)

# ---------- voice: trim silence in numpy so word timings stay exact
W = json.load(open('words.json'))
vo, words = [], []
for i in range(10):
    a, sr = sf.read(f'vo_{i}.wav'); env = np.abs(a) > 10 ** (-42 / 20)
    s0 = max(0, np.argmax(env) - int(0.02 * sr)); s1 = min(len(a), len(a) - np.argmax(env[::-1]) + int(0.04 * sr))
    sf.write(f'vt_{i}.wav', a[s0:s1], sr); vo.append((s1 - s0) / sr)
    words.append([[t, max(0, st - s0 / sr), max(0, en - s0 / sr)] for t, st, en in W[str(i)]['words']])
d = [max(v + 0.28, 1.6) for v in vo]; d[7] = 2.8; d[9] = vo[9] + 0.6
st = [sum(d[:i]) for i in range(10)]; T = sum(d)
vstart = [s + (0.0 if i == 0 else 0.05) for i, s in enumerate(st)]

# ---------- video beats: clip, start, slow, overlay, pre-filter, fade
BL = 'boxblur=14:2,eq=brightness=-0.2:saturation=0.7,'
HC = 'crop=820:1458:260:231,scale=1080:1920,'
B = [('n_chest.mp4', 0.0, 1.0, 'o1', '', False), ('n_wade.mp4', 0.0, 1.0, 'o2', BL, True),
     ('n_warm.mp4', 0.0, 1.0, 'r0', '', True), ('n_spring.mp4', 0.0, 1.0, 'r1', 'crop=900:1600:90:0,scale=1080:1920,', True),
     ('n_walk2.mp4', 0.0, 1.0, 'r2', '', True), ('n_booties.mp4', 1.25, 2.0, 'r3', 'SLOW', True),
     ('n_hood.mp4', 0.0, 1.0, 'r4', 'crop=820:1458:260:0,scale=1080:1920,', True), ('n_hood.mp4', 1.0, 1.0, 'o8', HC + BL, True),
     ('n_walkout.mp4', 0.0, 1.0, 'o8b', BL, True), ('n_chest.mp4', 0.0, 1.0, 'o9', 'LOOP', True)]
FADE = 'format=rgba,fade=t=in:st=0.03:d=0.15:alpha=1'
OVF = "overlay=x=0:y='if(lt(t,0.18),max(0,46*(0.18-t)/0.15),0)'"
REB = [int(x) for x in os.environ.get('REBUILD', '0,1,2,3,4,5,6,7,8,9').split(',')]
for i, (clip, ss, k, ov, ex, fade) in enumerate(B):
    if i not in REB and os.path.exists(f'b{i}.mp4'): continue
    cap = f'[1:v]{FADE}[c];[v][c]{OVF}' if fade else '[1:v]format=rgba[c];[v][c]overlay=0:0'
    ovin = ['-loop', '1', '-t', f'{d[i] + 0.5:.3f}', '-i', f'{ov}.png']
    if ex == 'LOOP':
        pre = (f'[0:v]trim=start=0.25,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=6,trim=0:{d[i]:.3f},setpts=PTS-STARTPTS,format=yuv420p[mv];'
               f'[2:v]format=yuva420p,fade=t=in:st={d[i] - 0.40:.3f}:d=0.35:alpha=1[st];[mv][st]overlay=0:0:eof_action=pass[v]')
        enc(['-i', clip, *ovin, '-loop', '1', '-framerate', '30', '-t', f'{d[i] + 0.3:.3f}', '-i', 'f0.png', '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
    elif ex == 'SLOW':
        a = 1.7; b = d[i] - a
        pre = (f'[0:v]trim=start={ss},setpts={k}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc,trim=0:{a:.3f},setpts=PTS-STARTPTS,format=yuv420p[sa];'
               f'[2:v]trim=0:0.95,setpts=1.45*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=blend,tpad=stop_mode=clone:stop_duration=2,trim=0:{b:.3f},setpts=PTS-STARTPTS,format=yuv420p[sb];'
               f'[sa][sb]concat=n=2:v=1:a=0[v]')
        enc(['-i', clip, *ovin, '-i', 'n_bstand.mp4', '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
    else:
        pre = f'[0:v]{ex}trim=start={ss},setpts={k}*(PTS-STARTPTS),tpad=stop_mode=clone:stop_duration=6,trim=0:{d[i]:.3f},setpts=PTS-STARTPTS[v]'
        enc(['-i', clip, *ovin, '-filter_complex', f'{pre};{cap}', '-t', f'{d[i]:.3f}'], f'b{i}.mp4')
open('list.txt', 'w').write(''.join(f'file b{i}.mp4\n' for i in range(10)))
run('-f', 'concat', '-i', 'list.txt', '-c', 'copy', 'v.mp4')

# ---------- subtitles (ASS), chunked, digits instead of spelled numbers, no trailing full stops or commas
NUM = {'seventy-five': '75', 'sixty-eight': '68', 'fifty-two': '52', 'sixty': '60', 'three-two': '3/2', 'four-three': '4/3', 'five-four': '5/4'}
SUBY = [1300, 1300, 1300, 1300, 800, 800, 1300, 1300, 1345, 1300]
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h}:{m:02d}:{s:05.2f}'
ev = []
for i in range(10):
    toks = []
    for t, a0, a1 in words[i]:
        if re.fullmatch(r"[^\w']+", t):
            if toks: toks[-1][0] += t.strip()
            continue
        if toks and toks[-1][0].endswith('-'): toks[-1][0] += t; toks[-1][2] = a1; continue
        toks.append([t, a0, a1])
    # phrases split at punctuation; long phrases halved; 1-word phrases merged into a short neighbour
    phrases, cur = [], []
    for w in toks:
        cur.append(w)
        if re.search(r'[?,.]$', w[0]): phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    merged = []
    for ph in phrases:
        if merged and len(ph) == 1 and len(merged[-1]) <= 2 and not merged[-1][-1][0].endswith(('?', '.')):
            merged[-1] = merged[-1] + ph
        else:
            merged.append(ph)
    chunks = []
    for ph in merged:
        if len(ph) <= 4: chunks.append(ph)
        else:
            h = (len(ph) + 1) // 2; chunks += [ph[:h], ph[h:]]
    for c in chunks:
        txt = ' '.join(w[0] for w in c)
        for kx, v in NUM.items(): txt = re.sub(kx, v, txt, flags=re.I)
        txt = re.sub(r'[.,]+$', '', txt.strip())
        ev.append([vstart[i] + c[0][1], vstart[i] + c[-1][2] + 0.15, st[i] + d[i], SUBY[i], txt])
lines = []
for j, (s0, s1, lim, y, txt) in enumerate(ev):
    nxt = ev[j + 1][0] if j + 1 < len(ev) else 1e9
    s1 = min(s1, lim, nxt - 0.02)
    lines.append(f"Dialogue: 0,{ts(s0)},{ts(s1)},Sub,,0,0,0,,{{\\an8\\pos(540,{y})\\fad(60,0)\\fscx92\\fscy92\\t(0,120,\\fscx100\\fscy100)}}{txt}")
ev = lines
ass = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n[V4+ Styles]\n"
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
       "Style: Sub,Rubik,64,&H00FFFFFF,&H00FFFFFF,&H00201820,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,8,140,140,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + '\n'.join(ev) + '\n')
open('subs.ass', 'w').write(ass)
run('-i', 'v.mp4', '-vf', f'subtitles=subs.ass:fontsdir={R}/fonts', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', 'vs.mp4')

# ---------- music window by RMS (highest-energy T seconds)
raw = sp.run([F, '-loglevel', 'error', '-i', 'ride.mp3', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
m = np.frombuffer(raw, np.int16).astype(float); hop = 4000
rms = np.array([np.sqrt(np.mean(m[k:k + hop] ** 2)) for k in range(0, len(m) - hop, hop)])
win = int(np.ceil(T * 2)); best = int(np.argmax([rms[k:k + win].mean() for k in range(0, len(rms) - win)])) / 2
# ---------- mix: voice + constant quiet music, pad to video length, two-pass loudnorm
ins, fc = [], ''
for i in range(10):
    ins += ['-i', f'vt_{i}.wav']; ms = int(vstart[i] * 1000); fc += f'[{i + 2}:a]aresample=48000,adelay={ms}|{ms}[v{i}];'
fc += ''.join(f'[v{i}]' for i in range(10)) + 'amix=inputs=10:normalize=0,aformat=channel_layouts=stereo[vo];'
fc += f'[1:a]atrim={best:.2f}:{best + T:.2f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=0.022,afade=t=in:d=0.15,afade=t=out:st={T - 0.6:.2f}:d=0.6[m];[vo][m]amix=inputs=2:normalize=0,apad,atrim=0:{T:.3f}[a]'
run('-i', 'vs.mp4', '-i', 'ride.mp3', *ins, '-filter_complex', fc, '-map', '[a]', '-c:a', 'pcm_s16le', 'mix.wav')
meas = sp.run([F, '-hide_banner', '-i', 'mix.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
J = json.loads(meas[meas.rindex('{'):meas.rindex('}') + 1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}:"
      f"measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true,aresample=48000")
run('-i', 'vs.mp4', '-i', 'mix.wav', '-filter_complex', f'[1:a]{ln}[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'wetsuit_v11.mp4')
info = {'T': round(T, 2), 'd': [round(x, 2) for x in d], 'music_start': best, 'loudnorm_in': J['input_i'], 'subs': len(ev)}
json.dump(info, open('info.json', 'w')); print('BUILD_OK', info)
