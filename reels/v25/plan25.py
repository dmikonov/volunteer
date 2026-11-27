"""Timeline + VO assembly for reel 25. Pieces cut from Edge Hebrew TTS lines at measured silences."""
import json, subprocess as sp, sys
D = '/home/claude/work/series/reels/guess25'
# piece: (file, start, end) per voice, measured by silencedetect -40 dB
P = {'E': {'1a': ('E1', .225, 1.814), '1b': ('E1', 2.806, 4.230), '2a': ('E2b', .226, .693), '2b': ('E2b', 1.730, 2.688),
           '2c': ('E2b', 3.055, 3.902), '3a': ('E3', .232, .835), '3b': ('E3b', .248, .895), '4': ('E4', .230, .848),
           '5a': ('E5', .258, 1.069), '5b': ('E5', 2.070, 2.913)},
     'F': {'1a': ('F1', .188, 1.612), '1b': ('F1', 2.552, 3.959), '2a': ('F2b', .251, .707), '2b': ('F2b', 1.708, 2.609),
           '2c': ('F2b', 2.984, 3.751), '3a': ('F3', .203, .744), '3b': ('F3b', .213, .776), '4': ('F4', .277, .845),
           '5a': ('F5', .190, .901), '5b': ('F5', 1.900, 2.806)}}
AT = {'1a': .12, '1b': 1.95, '2a': 3.42, '2b': 4.45, '2c': 5.85, '3a': 7.05, '3b': 7.95, '4': 9.13, '5a': 10.05, '5b': 11.10}
AT_V = {'F': {'3b': 8.02}}
SEGS = [('A1', 8, 40, 1.42, 'both', None), ('A2', 40, 60, 1.88, 'both', None), ('B1', 60, 66, .65, 'black', 1100),
        ('B2', 66, 22, .40, 'black', 1250), ('B3', 22, 50, 1.35, 'black', 1150), ('B4', 50, 80, 1.30, 'black', 1300),
        ('C1', 80, 139, .94, 'pink', 1050), ('C2', 139, 148, .56, 'pink', 1000), ('D', 148, 157, .60, 'pink', 950),
        ('F', 157, 157, .76, 'pink', 950), ('D2', 157, 170, .80, 'pink', 1100), ('E', 170, 191, 1.84, 'pink', 1350)]
NI = {'C1', 'C2', 'D', 'D2'}
tl = {'segs': [{'name': n, 'a': a, 'b': b, 'dur': d, 'cam': c, 'ni': n in NI, **({'w': w} if w else {})} for n, a, b, d, c, w in SEGS]}
T = sum(s[3] for s in SEGS)
tl.update({'flash': [9.10], 'hook_off': 1.80, 'mark_off': 3.0, 'end_on': 9.95, 'end_off': 11.97, 'loop': 0.30, 'blur': [122, 123, 124, 134],
           'badges': {'b1': {'on': -0.3, 'off': 7.0, 'x': 3.42}, 'b2': {'on': 1.20, 'off': 9.95, 'x': 9.10, 'hide': [[3.95, 5.70]]}},
           'chip': [[0.25, 3.30], [4.40, 5.70]],
           'subs': [['1b', 1.95, 3.42], ['2a', 3.42, 3.97], ['2b', 4.45, 5.70], ['2c', 5.85, 6.85], ['3a', 7.05, 7.80],
                    ['3b', 7.95, 8.95], ['4', 9.13, 9.95]],
           'vo_at': AT, 'total': T})
json.dump(tl, open(f'{D}/tl.json', 'w'), indent=1, ensure_ascii=False)
# VO tracks (48 kHz mono), one per voice
for v, pcs in P.items():
    ins, fl = [], []
    for i, (k, (f, a, b)) in enumerate(pcs.items()):
        ins += ['-i', f'{D}/vo/{f}.mp3']
        fl.append(f'[{i}:a]atrim={a - .03:.3f}:{b + .06:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={b - a + .04:.3f}:d=0.05,adelay={int(AT_V.get(v, {}).get(k, AT[k]) * 1000)}:all=1[p{i}]')
    fl.append(''.join(f'[p{i}]' for i in range(len(pcs))) + f'amix=inputs={len(pcs)}:normalize=0,apad,atrim=0:{T:.3f}[o]')
    sp.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[o]', '-ac', '1', f'{D}/vo_{v}.wav'], check=True)
print('total', round(T, 2))
