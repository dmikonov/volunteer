"""Mix + overlay from ovplan.json (made by ov_png.py). usage: python3 ov_ff.py <workdir>"""
import json, os, sys, re, subprocess as sp
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); A = os.environ.get('S17', '/s17') + '/tip1'
P = json.load(open(f'{W}/ovplan.json')); ON, pos, wh, imp, pops, T = P['ON'], P['pos'], P['wh'], P['imp'], P['pops'], P['T']
ains = ['-i', f'{W}/vo.wav', '-stream_loop', '-1', '-i', f'{A}/music.wav']
MV = S.get('music_vol', 0.9)  # Dima 18.10: music was inaudible at 0.30
afc = [f"[1:a]volume={MV},atrim=0:{T + 1.5},afade=t=in:d=0.3,afade=t=out:st={max(0, T - 1.2):.2f}:d=1.2[mu]", "[0:a]asplit=2[vo][k0]", f"[k0]apad=whole_dur={T + 2}[key]", f"[mu][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300,atrim=0:{T}[md]"]  # sidechain output ends ~0.65 s early: feed 1.5 s extra, trim after (reviewer 18.10)  # apad: reviewer 18.10, music was cut 0.6 s early
mixin = ['[vo]', '[md]']; k = 2
for fn, times, vol in (('whoosh.wav', wh, 0.55), ('impact.wav', imp, 0.8), ('pop.wav', pops, 0.45)):
    for tt in times:
        ains += ['-i', f'{A}/{fn}']; afc.append(f"[{k}:a]adelay={int(max(0, tt) * 1000)}|{int(max(0, tt) * 1000)},volume={vol}[x{k}]"); mixin.append(f'[x{k}]'); k += 1
afc.append(f"{''.join(mixin)}amix=inputs={len(mixin)}:normalize=0:duration=longest,atrim=0:{T},volume=-1.6dB,alimiter=limit=0.84[aout]")  # ~-14.5 LUFS, <= -1.5 dBTP
sp.run(['ffmpeg', '-v', 'error', '-y'] + ains + ['-filter_complex', ';'.join(afc), '-map', '[aout]', '-t', str(T), '-ar', '48000', '-ac', '2', f'{W}/mix.wav'], check=True)
ins = ['-i', f'{W}/cat.mp4', '-i', f'{W}/mix.wav']; fcs = []; prev = '0:v'
for i, (kk, a, b) in enumerate(ON):
    # each image exists only inside its window: decode cost ~ window length, not the whole reel
    ins += ['-loop', '1', '-framerate', '25', '-t', f'{max(0.04, b - a):.3f}', '-i', f'{W}/ov/{kk}.png']
    fcs.append(f"[{i + 2}:v]format=rgba,setpts=PTS+{a:.3f}/TB[o{i}]")
    fcs.append(f"[{prev}][o{i}]overlay={pos[kk][0]}:{pos[kk][1]}:eof_action=pass:repeatlast=0[v{i}]"); prev = f'v{i}'
OUT = f"{W}/{S['out']}"
sp.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fcs), '-map', f'[{prev}]', '-map', '1:a', '-threads', '1', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-maxrate', '18M', '-bufsize', '36M', '-pix_fmt', 'yuv420p', '-r', '25', '-c:a', 'aac', '-b:a', '192k', '-t', str(T), '-movflags', '+faststart', OUT], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', OUT, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]); g = round(-14.5 - I, 2)  # reviewer 18.10: -14.5 LUFS, true peak <= -1.5 dBTP
if abs(g) > 0.2:
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT, '-c:v', 'copy', '-af', f'volume={g}dB,alimiter=limit=0.84', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', OUT + '.t.mp4'], check=True); os.replace(OUT + '.t.mp4', OUT)
print('done', OUT, T, 'lufs before', I, 'gain', g)
