import json, subprocess as sp
D = '/home/claude/work/series/reels/r27'
P = {'1a': ('L1', .214, 1.650), '1b': ('L1', 2.111, 4.876), '3a': ('L3', .215, 1.253), '3b': ('L3', 1.614, 3.415), '3c': ('L3', 4.348, 5.697),
     '4a': ('L4', .194, 1.370), '4c': ('L4', 2.943, 4.570), '4d': ('L4', 5.506, 7.174), '5a': ('L5', .216, 1.475), '5b': ('L5', 1.795, 2.791),
     '5c': ('L5', 3.738, 5.050), '4b': ('L4', 1.714, 2.553), '6b': ('L6n', .229, 1.966), '6c': ('L6n', 2.907, 3.580)}
AT = {'1a': .10, '1b': 1.74, '3a': 4.80, '3b': 6.00, '3c': 8.00, '4a': 9.65, '4b': 11.00, '4c': 12.00, '4d': 13.83, '5a': 15.80, '5b': 17.25, '5c': 18.50, '6b': 20.10, '6c': 22.05}
T = 23.4
ins, fl = [], []
for i, (k, (f, a, b)) in enumerate(P.items()):
    ins += ['-i', f'{D}/vo/{f}.mp3']
    fl.append(f'[{i}:a]atrim={a - .03:.3f}:{b + .06:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={b - a + .04:.3f}:d=0.05,adelay={int(AT[k] * 1000)}:all=1[p{i}]')
fl.append(''.join(f'[p{i}]' for i in range(len(P))) + f'amix=inputs={len(P)}:normalize=0,apad,atrim=0:{T:.3f}[o]')
sp.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fl), '-map', '[o]', '-ac', '1', f'{D}/vo.wav'], check=True)
END = {k: AT[k] + P[k][2] - P[k][1] for k in P}
print({k: round(v, 2) for k, v in END.items()})
C82, C121 = '/mnt/user-data/uploads/C0082.mp4', '/mnt/user-data/uploads/C0121.mp4'
SH = "text-shadow:0 3px 18px rgba(0,0,0,.55),0 1px 4px rgba(0,0,0,.7)"
def line(t, fs, color='#F5F1F7', ltr=False, w=800):
    d = "direction:ltr;unicode-bidi:isolate;" if ltr else ""
    return f"<div dir=rtl style='position:absolute;left:0;right:0;top:0;text-align:center;font-weight:{w};font-size:{fs}px;line-height:1.05;color:{color};{d}{SH}'>{t}</div>"
scrim = "<div style='position:absolute;inset:0;background:rgba(30,22,28,.42)'></div>"
cards = [{"html": scrim, "t0": 4.70, "t1": 22.5, "y": 0, "h": 1920}]
mark = f"<div style='position:absolute;left:0;right:0;top:0;text-align:center;font-weight:800;font-size:46px;direction:ltr;{SH}'>Surf<span style='color:#00CDFE'>Tribe</span></div>"
cards += [{"html": mark, "t0": -1, "t1": 4.55, "y": 250, "h": 80},
          {"html": line('אף אחד לא אומר לכם את זה', 54, '#00CDFE'), "t0": -1, "t1": 4.55, "y": 330, "h": 90},
          {"html": f"<div dir=rtl style='position:absolute;left:0;right:0;top:0;text-align:center;font-weight:800;font-size:92px;line-height:1.08;{SH}'>בישראל לא צריך<br>חליפה עבה מ-<span style='direction:ltr;unicode-bidi:isolate'>3/2</span></div>", "t0": 1.70, "t1": 4.55, "y": 410, "h": 230}]
def beat(t_lab, t_num, t_gear, t_end, lab, num, gear, numsize=170):
    return [{"html": line(lab, 60, '#00CDFE'), "t0": t_lab, "t1": t_end, "y": 380, "h": 90},
            {"html": line(num, numsize, ltr=True), "t0": t_num, "t1": t_end, "y": 480, "h": 230},
            {"html": line('מעלות במים', 40, '#CFC6D3', w=600), "t0": t_num, "t1": t_end, "y": 690, "h": 60},
            {"html": line(gear, 70), "t0": t_gear, "t1": t_end, "y": 760, "h": 110}]
cards += beat(4.80, 6.00, 8.00, 9.45, 'יוני עד אוקטובר', '25°-29°', 'בגד ים או לייקרה')
cards += beat(9.65, 12.00, 13.83, 15.62, 'נובמבר עד ינואר · אפריל ומאי', '19°-23°', 'ספרינג 2 מ״מ')
cards += beat(15.80, 17.25, 18.50, 19.92, 'רק בפברואר ומרץ', '17.5°', '<span style="direction:ltr;unicode-bidi:isolate">3/2</span> מלאה', 200)
cards += [{"html": line('מנובמבר', 130), "t0": 20.10, "t1": 22.95, "y": 400, "h": 170},
          {"html": line('כבר צריך ספרינג', 76), "t0": 20.60, "t1": 22.95, "y": 570, "h": 110},
          {"html": "<div style='position:absolute;left:0;right:0;top:0;text-align:center'><span dir=rtl style='display:inline-block;background:#00CDFE;color:#2D242A;padding:14px 40px;border-radius:999px;font-weight:800;font-size:60px'>שמרו את זה</span></div>", "t0": 22.0, "t1": 22.95, "y": 760, "h": 120},
          {"html": mark, "t0": 20.10, "t1": 22.95, "y": 920, "h": 80}]
IMG = D + '/img/'
def C(src, a, b, cx, cy, z, **k): return dict(src=src, **{'in': a, 'out': b}, rotate=90, cx=cx, cy=cy, zoom=z, **k)
def P(f, a, b): return {"src": IMG + f, "in": a, "out": b, "rotate": 0, "cx": .5, "cy": .5, "zoom": 1.0}
shots = [C(C82, 0.8, 3.0, .66, .41, 1.55), P('full_a.mp4', 0, 2.4),
         C(C82, 5.56, 7.68, .52, .43, 1.6), C(C82, 0.8, 3.0, .62, .38, 1.15), C(C121, 0.0, 0.70, .45, .42, 1.15),
         P('spring_a.mp4', 0, 2.5), P('spring_b.mp4', 0, 2.5), P('spring_a.mp4', 2.0, 3.0),
         P('full_b.mp4', 0, 2.2), P('full_a.mp4', 0.3, 2.5),
         C(C82, 0.0, 2.2, .70, .41, 1.55)]
t = sum(s['out'] - s['in'] for s in shots)
shots.append(C(C82, 5.56, 5.56 + round(T - t, 3), .52, .43, 1.6))
edl = {"out": f"{D}/r27_silent.mp4", "loop": 0.3, "a_shift": 7.0, "shots": shots, "cards": cards, "subs": []}
json.dump(edl, open(f'{D}/edl.json', 'w'), ensure_ascii=False, indent=1)
acc = 0
for s in shots: print(round(acc, 2), round(acc + s['out'] - s['in'], 2), s['src'][-9:]); acc += s['out'] - s['in']
