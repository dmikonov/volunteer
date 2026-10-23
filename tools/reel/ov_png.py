import json, os, sys, re, base64, subprocess as sp
import cv2, numpy as np
from playwright.sync_api import sync_playwright  # split 19.10: ov_png.py renders plates, ov_ff.py mixes (no HF sandbox)
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); LANG = S['lang']; HE = LANG == 'he'; A = '/s17/tip1'
TL = json.load(open(f'{W}/tl.json')); L = TL['L']; T = TL['T']
segs = json.load(open(f'{W}/segs.json')) if os.path.exists(f'{W}/segs.json') else []
cuts = [0.0] + [round(l['t0'] - 0.1, 3) for l in L[1:]] + [T]
REALCUTS = False  # 21.10: real line starts from the encoded segments (frame-rounded); planned cuts drift up to ~2 frames late
try:
  if segs and os.path.exists(f'{W}/seg/00.mp4'):
    import glob as _g
    _fr = [int(cv2.VideoCapture(f).get(7)) for f in sorted(_g.glob(f'{W}/seg/[0-9][0-9].mp4'))]
    if len(_fr) == len(segs) and all(_fr):
        _st = np.cumsum([0] + _fr) / 25.0; _first = {}
        for _j, _s in enumerate(segs): _first.setdefault(_s['line'], float(_st[_j]))
        if all(l['k'] in _first for l in L):
            cuts = [0.0] + [round(_first[l['k']], 4) for l in L[1:]] + [T]; REALCUTS = True
    if REALCUTS and os.path.exists(f'{W}/cat.mp4'):  # refine on the picture itself: strongest frame change within +-4 frames
        _c = cv2.VideoCapture(f'{W}/cat.mp4'); _g0 = []
        while True:
            _ok, _f = _c.read()
            if not _ok: break
            _g0.append(cv2.resize(cv2.cvtColor(_f, cv2.COLOR_BGR2GRAY), (54, 96)).astype(np.float32))
        _dd = [0.0] + [float(np.abs(_g0[i] - _g0[i - 1]).mean()) for i in range(1, len(_g0))]
        _pts = [float(x.strip(',').split(',')[0]) for x in sp.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'frame=pts_time', '-of', 'csv=p=0', f'{W}/cat.mp4'], capture_output=True, text=True).stdout.split() if x.strip(',').strip()]
        if len(_pts) != len(_dd): _pts = [i / 25.0 for i in range(len(_dd))]  # concat timestamps are not on the 1/25 grid: use real pts
        for _i in range(1, len(cuts) - 1):
            _k = int(np.searchsorted(_pts, cuts[_i])); _w = [j for j in range(_k - 4, _k + 5) if 0 < j < len(_dd)]
            if _w:
                _b = max(_w, key=lambda j: _dd[j])
                if _dd[_b] > 8: cuts[_i] = round(round(_pts[_b] * 25) / 25.0, 4)
except Exception as _e: print('realcuts skipped', _e)
print('realcuts', REALCUTS, cuts)
CY, AM, NAVY, RED, GRN = '#00d4ff', '#f5a623', 'rgba(10,18,38,.80)', '#FF5150', '#3DDC84'
XI = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{RED}'/><path d='M20 20L44 44M44 20L20 44' stroke='#fff' stroke-width=8 stroke-linecap=round/></svg>"
CK = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{GRN}'/><path d='M17 33L28 44L47 22' stroke='#fff' stroke-width=8 fill=none stroke-linecap=round stroke-linejoin=round/></svg>"
WARN = f"<svg width=64 height=64 viewBox='0 0 64 64' style='vertical-align:-10px'><circle cx=32 cy=32 r=30 fill='{RED}'/><path d='M32 14V38' stroke='#fff' stroke-width=8 stroke-linecap=round/><circle cx=32 cy=49 r=5 fill='#fff'/></svg>"
ICON = {'X': XI, 'CK': CK, 'WARN': WARN, None: None}
TITLES = S['titles']; RECAP = S['recap']; LAST = L[-1]['k']
F = base64.b64encode(open('/s17/Rubik.ttf', 'rb').read()).decode()
DIR = 'rtl' if HE else 'ltr'; FS = 80 if HE else 70
def page(body):
    return f"""<!doctype html><html><head><meta charset=utf-8><style>@font-face{{font-family:R;src:url(data:font/ttf;base64,{F});font-weight:300 900}}
html,body{{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}}*{{font-family:R;box-sizing:border-box}}
.blk{{position:absolute;top:330px;left:0;right:0;text-align:center;direction:{DIR};transform-origin:50% 40%}}
.plate{{display:inline-block;white-space:nowrap;padding:26px 34px;border-radius:26px;background:{NAVY};font-weight:800;font-size:{FS}px;line-height:1.15;text-box:trim-both cap alphabetic;color:#fff}}
.plate.sm{{font-size:{62 if HE else 56}px}}
.n{{display:inline-block;width:92px;height:92px;border-radius:50%;background:{CY};color:#0a1226;font-weight:800;font-size:62px;line-height:92px;text-align:center;margin-bottom:14px}}
.sub{{position:absolute;top:1298px;left:0;right:0;text-align:center;direction:{DIR}}}
.sub span{{display:inline-block;white-space:nowrap;padding:18px 28px;border-radius:20px;background:{NAVY};font-weight:800;font-size:50px;line-height:1;text-box:trim-both cap alphabetic;color:#fff}}
.mark{{position:absolute;top:240px;left:0;right:0;text-align:center;direction:ltr}}
.mark span.b{{display:inline-block;padding:16px 26px;border-radius:20px;background:{NAVY};font-weight:800;font-size:48px;line-height:1;text-box:trim-both cap alphabetic;color:#fff}}
.rc{{position:absolute;top:{S.get('recap_top', 330)}px;left:0;right:0;text-align:center;direction:{DIR}}}
.rc .box{{display:inline-block;width:620px;padding:26px 34px 30px;border-radius:30px;background:{NAVY};text-align:{'right' if HE else 'left'}}}
.rc h{{display:block;font-weight:800;font-size:{58 if HE else 50}px;color:{CY};margin-bottom:18px;text-align:center}}
.rc .row{{font-weight:800;font-size:{52 if HE else 44}px;color:#fff;margin:12px 0;white-space:nowrap}}
.flw{{position:absolute;top:{S.get('follow_top', 760)}px;left:0;right:0;text-align:center}}
.flw span{{display:inline-block;padding:24px 64px;border-radius:22px;font-weight:800;font-size:56px;line-height:1;text-box:trim-both cap alphabetic;color:#fff;background:#0095f6;box-shadow:0 6px 24px rgba(0,0,0,.35)}}
.flw span.on{{background:#262a36;color:#fff}}
.tz{{position:absolute;top:{S.get('recap_top', 330)}px;left:0;right:0;text-align:center;direction:{DIR}}}
.tz .box{{display:inline-block;max-width:600px;padding:28px 36px 32px;border-radius:30px;background:{NAVY};text-align:center}}
.tz h{{display:block;font-weight:800;font-size:{58 if HE else 50}px;color:{CY};margin-bottom:16px}}
.tz .t{{display:block;font-weight:800;font-size:{64 if HE else 56}px;color:#fff;line-height:1.15;text-wrap:balance}}
.g2{{position:absolute;top:0;left:0;width:1080px;height:700px;background:linear-gradient(180deg,rgba(45,36,42,.50) 0px,rgba(45,36,42,.32) 330px,rgba(45,36,42,.12) 520px,rgba(45,36,42,0) 700px)}}
.t2,.lab2{{position:absolute;top:250px;left:0;right:0;display:flex;justify-content:center;direction:{DIR}}}
.t2 span.x{{display:inline-block;max-width:620px;text-align:center;font-weight:800;font-size:92px;line-height:1.02;color:#fff;text-wrap:balance;text-shadow:0 3px 6px rgba(45,36,42,.6),0 6px 22px rgba(45,36,42,.5)}}
.lab2{{top:300px}} .lab2 span.x{{display:inline-flex;align-items:center;gap:18px;white-space:nowrap;font-weight:800;font-size:64px;line-height:1;color:#fff;text-shadow:0 3px 6px rgba(45,36,42,.6),0 6px 22px rgba(45,36,42,.5)}}
.lab2 svg{{flex:none;filter:drop-shadow(0 4px 8px rgba(45,36,42,.6))}}
.s2{{position:absolute;top:{S.get('v2_sub_top', 1358)}px;left:0;right:0;display:flex;justify-content:center;direction:{DIR}}}
.s2 span{{position:relative;display:inline-block;white-space:nowrap;font-weight:800;font-size:64px;line-height:1;color:#fff;text-shadow:0 3px 6px rgba(45,36,42,.6),0 6px 22px rgba(45,36,42,.5)}}
.s2 span::before{{content:'';position:absolute;inset:-34px -60px;z-index:-1;background:radial-gradient(closest-side,rgba(45,36,42,.55),rgba(45,36,42,.4) 55%,rgba(45,36,42,0))}}
.tz .f{{display:inline-block;white-space:nowrap;margin-top:26px;padding:14px 24px;border-radius:18px;background:#0095f6;font-weight:800;font-size:{38 if HE else 31}px;color:#fff;line-height:1;text-box:trim-both cap alphabetic}}
</style></head><body>{body}</body></html>"""
if S.get('app_notitle'):
    for kk in S.get('app_lines', []): TITLES.pop(kk, None)
cards = {}
for l in L:
    if l['k'] == LAST or l['k'] not in TITLES: continue
    a, b, n, ic = TITLES[l['k']]; ic = ICON[ic]
    num = f"<div class=n>{n}</div><br>" if n else ''
    acc = CY if S.get('hook_cy') else (AM if l['k'] in ('L1', 'L2') else CY)  # 23.10 formula: line 2 cyan
    icon = f"{ic}&nbsp;" if ic else ''
    sm = ' sm' if l['k'] in S.get('app_lines', []) else ''
    inner = f"{num}<div class='plate{sm}'>{icon}{a}" + (f"<br><span style='color:{acc}'>{b}</span>" if b else '') + "</div>"  # 21.10: one-line card when b is empty (bridge line)
    for tag, sc in (('a', 1.22), ('b', 0.95), ('c', 1.0)):
        top = f"top:{S.get('app_top', 330)}px;" if sm else (f"top:{S['ttop'][l['k']]}px;" if l['k'] in S.get('ttop', {}) else '')  # 20.10: per-line card top (keep faces clear)
        cards[f"T{l['k']}{tag}"] = f"<div class=blk style='{top}transform:scale({sc})'>{inner}</div>"
rows = ''.join(f"<div class=row>{CK}&nbsp;&nbsp;{x}</div>" for x in RECAP[1])
for tag, sc in (('a', 1.15), ('b', 0.97), ('c', 1.0)):
    cards[f'RECAP{tag}'] = f"<div class=rc style='transform:scale({sc});transform-origin:50% 30%'><div class=box><h>{RECAP[0]}</h>{rows}</div></div>"
if S.get('teaser'):  # 21.10 new concept: tomorrow teaser on the last line instead of the recap
    tz = S['teaser']
    for tag, sc in (('a', 1.0), ('b', 1.0), ('c', 1.0)):
        cards[f'RECAP{tag}'] = f"<div class=tz><div class=box><h>{tz[0]}</h><span class=t>{tz[1]}</span>" + (f"<span class=f>{tz[2]}</span>" if len(tz) > 2 else '') + "</div></div>"
if S.get('badge'):  # 21.10: daily badge for the whole reel (replaces the SurfTribe mark)
    bd = S['badge']; bdir = 'rtl' if HE else 'ltr'
    brand = f"Surf<span style='color:{CY}'>Tribe</span>&nbsp;&nbsp;·&nbsp;&nbsp;"  # checklist 10: brand visible in the first 3 s and at the end
    cards['BADGE'] = f"<div class=mark><span class=b style='font-size:44px'>{brand}<span dir={bdir}>{bd[0]} <span style='color:{CY}'>{bd[1]}</span></span></span></div>"
if S.get('follow'):  # 21.10 EN concept: animated Follow button under the follow card
    fl = S['follow']
    cards['FBTN0'] = f"<div class=flw><span>{fl.get('btn', 'Follow')}</span></div>"
    cards['FBTN1'] = f"<div class=flw><span style='transform:scale(.92);display:inline-block;background:#0077cc'>{fl.get('btn', 'Follow')}</span></div>"
    cards['FBTN2'] = f"<div class=flw><span class=on>{fl.get('done', 'Following')} &#10003;</span></div>"
cards['MARK'] = f"<div class=mark><span class=b>Surf<span style='color:{CY}'>Tribe</span></span></div>"
cards['MARKA'] = f"<div class=mark style='top:{S.get('app_top', 330) - 90}px'><span class=b>Surf<span style='color:{CY}'>Tribe</span></span></div>"
for e in S.get('extra', []): cards[e['k']] = e['html']  # 20.10: custom overlays (arrow etc.)
if S.get('logo'):  # 23.10 Dima: new round SurfTribe logo, small, in the corner for the whole reel
    _lg = S['logo'] if isinstance(S['logo'], dict) else {}
    cards['LOGO'] = (f"<div style='position:absolute;top:{_lg.get('top', 240)}px;left:{_lg.get('left', 60)}px;width:{_lg.get('size', 124)}px;height:{_lg.get('size', 124)}px;border-radius:50%;"
                     f"background:#2D242A;display:flex;flex-direction:column;align-items:center;justify-content:center;direction:ltr;box-shadow:0 2px 10px rgba(0,0,0,.35)'>"
                     f"<span style='font:800 {int(_lg.get('size', 124) * 0.27)}px R;line-height:.92;color:#fff'>Surf</span>"
                     f"<span style='font:800 {int(_lg.get('size', 124) * 0.27)}px R;line-height:.92;color:#00CDFE'>Tribe</span></div>")
cards['FLASH'] = "<div style='position:absolute;inset:0;background:rgba(255,255,255,.85)'></div>"
STOP = {'עם', 'על', 'את', 'של', 'לפני', 'the', 'a', 'to', 'of', 'with', 'your', 'from', 'and', 'at', 'over', 'when', 'you', 'is', 'off', 'on', 'in', 'by'}
subs = []
for l in L:
    toks = l['txt'].split(); Wd = l['words']
    if len(toks) != len(Wd): toks = [w[0] for w in Wd]
    phrases, curp = [], []
    for tok, w in zip(toks, Wd):
        curp.append((tok, w[1], w[2]))
        if tok.endswith(('.', ',', ':', '?')): phrases.append(curp); curp = []  # 20.10: split after ? too (keeps subtitles at full size)
    if curp: phrases.append(curp)
    for ph in phrases:
        if len(ph) <= 4 or len(' '.join(c[0] for c in ph)) <= 28: subs.append([' '.join(c[0] for c in ph), ph[0][1], ph[-1][2]]); continue
        best = None
        for cut in sorted(range(1, len(ph)), key=lambda c: abs(len(' '.join(x[0] for x in ph[:c])) - len(' '.join(x[0] for x in ph[c:])))):
            if ph[cut - 1][0].strip('.,:').lower() not in STOP: best = cut; break
        best = best or len(ph) // 2
        for part in (ph[:best], ph[best:]): subs.append([' '.join(c[0] for c in part), part[0][1], part[-1][2]])
clean = []
for i, (txt, s0, s1) in enumerate(subs):
    nxt = subs[i + 1][1] if i + 1 < len(subs) else s1 + 0.4
    lend = min([c for c in cuts if c > s0 + 0.05] + [T]) - 0.04
    tx = re.sub(r'[.,:]$', '', txt.strip())
    for k0, v0 in S.get('sub_replace', {}).items(): tx = tx.replace(k0, v0)
    if HE: tx = '\u200f' + tx  # 20.10: RLM so a line that starts with SurfTribe still reads right to left
    clean.append((tx, s0, min(nxt - 0.04, s1 + 0.5, lend)))  # 20.10: no one-frame double subtitle
APPW = [(cuts[[l['k'] for l in L].index(kk)], cuts[[l['k'] for l in L].index(kk) + 1]) for kk in S.get('app_lines', [])]
for i, (txt, s0, s1) in enumerate(clean):
    st = f" style='top:{S['app_sub_top']}px'" if S.get('app_sub_top') and any(a0 - 0.05 <= s0 < b0 for a0, b0 in APPW) else ''
    _li = max([j for j in range(len(L)) if cuts[j] <= s0 + 0.05] or [0])  # 21.10: per-line subtitle height (spec sub_top {"L3": 840}) to keep subs off the key detail
    if S.get('sub_top', {}).get(L[_li]['k']): st = f" style='top:{S['sub_top'][L[_li]['k']]}px'"
    cards[f'S{i:02d}'] = f"<div class=sub{st}><span>{txt}</span></div>"
V2 = S.get('style') == 'v2'  # 21.10 Dima: no plates/badges/buttons. Research of 22 surf-coaching hits: white text + soft shadow, 1-3 word step labels with drawn marks, <= 5 words on screen
V2X = "<svg width='64' height='64' viewBox='0 0 64 64'><path d='M12 12 L52 52 M52 12 L12 52' stroke='#2D242A' stroke-width='20' stroke-linecap='round'/><path d='M12 12 L52 52 M52 12 L12 52' stroke='#FF5150' stroke-width='12' stroke-linecap='round'/></svg>"
V2V = "<svg width='68' height='64' viewBox='0 0 68 64'><path d='M8 34 L26 52 L60 12' fill='none' stroke='#00E4FF' stroke-width='12' stroke-linecap='round' stroke-linejoin='round'/></svg>"
V2SUB = []
if V2:
    for kk in [k for k in cards if k.startswith(('T', 'RECAP', 'BADGE', 'FBTN', 'MARK', 'S'))]: cards.pop(kk)
    cards['GRAD'] = "<div class=g2></div>"
    for l in L:
        k = l['k']
        if k in TITLES and k != LAST:
            a, b, n, ic = TITLES[k]
            txt = a + (f" <span style='color:#00E4FF'>{b}</span>" if b else '')
            if ic: cards[f'T{k}c'] = f"<div class=lab2><span class=x>{V2X if ic in ('X', 'WARN') else V2V}<span>{txt}</span></span></div>"
            else: cards[f'T{k}c'] = f"<div class=t2{(' style=' + chr(39) + 'top:' + str(S['ttop'][k]) + 'px' + chr(39)) if k in S.get('ttop', {}) else ''}><span class=x>{txt}</span></div>"  # 23.10: v2 honours spec ttop (title off a key detail)
    if S.get('teaser'):
        tz = S['teaser']
        cards['RECAPc'] = f"<div class=t2><span class=x><span style='color:#00E4FF;font-size:64px'>{tz[0]}</span><br>{tz[1]}</span></div>"
    def _n(s): return re.sub(r"[^\w']", '', s.lower())
    for i, l in enumerate(L):
        chunks = S.get('v2subs', {}).get(l['k'], [])
        Wd = l['words']; toks = [_n(w[0]) for w in Wd]; starts = []
        for ch in chunks:
            cw = [_n(x) for x in ch.split()]
            hit = next((j for j in range(len(toks) - len(cw) + 1) if toks[j:j + len(cw)] == cw), None)
            if hit is None: print('V2 SUB NOT IN VOICE', l['k'], ch); continue
            starts.append((ch, Wd[hit][1]))
        for j, (ch, s0) in enumerate(starts):
            s1 = starts[j + 1][1] - 0.04 if j + 1 < len(starts) else cuts[i + 1] - 0.04
            V2SUB.append((f'S{len(V2SUB):02d}', ch, max(s0, cuts[i] + 0.04), s1))
    for kk, ch, s0, s1 in V2SUB: cards[kk] = f"<div class=s2><span>{ch}</span></div>"
os.makedirs(f'{W}/ov', exist_ok=True); pos = {}; boxes = {}
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    for k, h in cards.items():
        pg.set_content(page(h)); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(100)
        pg.evaluate("() => { for (const [sel, mx] of [['.sub span', 600], ['.plate', 620], ['.t2 span.x', 620], ['.lab2 span.x', 620], ['.s2 span', 620]]) for (const e of document.querySelectorAll(sel)) { let f = parseFloat(getComputedStyle(e).fontSize); while (e.getBoundingClientRect().width > mx && f > 24) { f -= 2; e.style.fontSize = f + 'px'; } } }")
        boxes[k] = pg.evaluate("() => [...document.querySelectorAll('.plate,.sub span,.mark span.b,.n,.rc .box,.tz .box,.flw span,.t2 span.x,.lab2 span.x,.s2 span')].map(e => {const r=e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.top), Math.round(r.bottom)]})")
        fn = f'{W}/ov/{k}.png'; pg.screenshot(path=fn, omit_background=True)
        im = cv2.imread(fn, cv2.IMREAD_UNCHANGED); ys, xs = (im[..., 3] > 0).nonzero()
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1; cv2.imwrite(fn, im[y0:y1, x0:x1]); pos[k] = (int(x0), int(y0))
    br.close()
bad = [(k, b) for k, bb in boxes.items() if not k.endswith(('a', 'b')) for b in bb if b[0] < 70 or b[1] > 850 or b[2] < 230 or b[3] > 1440]
print('safe-zone violations', bad)
ON = []; F1, F2 = 0.08, 0.16
for i, l in enumerate(L):
    a, b = cuts[i], cuts[i + 1]
    base = 'RECAP' if l['k'] == LAST else ('T' + l['k'] if l['k'] in TITLES else None)
    if base and S.get('pop'): ON += [(base + 'a', a, a + F1), (base + 'b', a + F1, a + F2), (base + 'c', a + F2, b)]
    elif base: ON.append((base + 'c', a, b))  # 21.10: no scale pop on cards (Dima 20.10: no 'pops'); also removes a 1-frame blank between a/b
    if i > 0 and S.get('flash'): ON.append(('FLASH', a - 0.02, a + 0.06))  # Dima 20.10: no white flashes unless spec flash=true
if S.get('badge'): ON.append(('BADGE', 0, T))
else: ON += [('MARK', 0, 3.0), ('MARK', cuts[-2], T)]
if S.get('follow'):
    fi = [l['k'] for l in L].index(S['follow']['line']); fa, fb = cuts[fi], cuts[fi + 1]; tp = fa + (fb - fa) * S['follow'].get('tap', 0.6)
    ON += [('FBTN0', fa + 0.12, tp), ('FBTN1', tp, tp + 0.12), ('FBTN2', tp + 0.12, fb)]
for e in S.get('extra', []):
    i = [l['k'] for l in L].index(e['line']); d0 = e.get('d0', 0.3); st = cuts[i + 1] + d0 if d0 < 0 else cuts[i] + d0  # 21.10: d0 < 0 = seconds before the line's end
    ON.append((e['k'], st, cuts[i] + e['d1'] if 'd1' in e else cuts[i + 1]))
    if e.get('cut_title'): ON = [(k, a, min(b, st)) if k.startswith('T' + e['line']) else (k, a, b) for k, a, b in ON]  # 21.10: line card ends where the overlay (recap) starts
for kk in S.get('app_lines', []):
    i = [l['k'] for l in L].index(kk)
    if not S.get('app_notitle') and not S.get('no_marka'): ON.append(('MARKA', cuts[i], cuts[i + 1]))
_B = []  # 20.10: snap card switches to the real cut frames, detected in cat.mp4 (frame difference peaks)
if os.path.exists(f'{W}/cat.mp4'):
    _c = cv2.VideoCapture(f'{W}/cat.mp4'); _fps = _c.get(5) or 25; _pv = None; _d = []
    while True:
        _ok, _fr = _c.read()
        if not _ok: break
        _g = cv2.resize(cv2.cvtColor(_fr, cv2.COLOR_BGR2GRAY), (54, 96)).astype(np.float32)
        _d.append(0.0 if _pv is None else float(np.abs(_g - _pv).mean())); _pv = _g
    _med = float(np.median(_d)) if _d else 0
    _B = [i / _fps for i in range(1, len(_d) - 1) if _d[i] > max(12.0, 4 * _med) and _d[i] >= _d[i - 1] and _d[i] >= _d[i + 1]]
def _snap(t, end=False):
    if REALCUTS: return t if t < 0.5 else (round(t - 0.004, 4) if end else round(t + 0.004, 4))
    c = min(_B, key=lambda x: abs(x - t)) if _B else t
    return t if abs(c - t) > 0.13 or t < 0.5 else (round(c - 0.004, 4) if end else round(c + 0.004, 4))  # verified 20.10: card on the cut frame
_ks = [e['k'] for e in S.get('extra', [])]
ON = [(k, _snap(a) if not k.endswith('b') else a, _snap(b, True) if not k.endswith('a') else b) if (k.startswith(('T', 'RECAP', 'MARK')) or k in _ks) and k != 'BADGE' and k not in ('TL1a', 'TL1b') else (k, a, b) for k, a, b in ON]
for _i, (k, a, b) in enumerate(ON):  # keep the pop frames (a, b) glued to the snapped start
    if k.startswith(('T', 'RECAP')) and k.endswith('a'):
        base = k[:-1]; ON = [(kk, aa, bb) for kk, aa, bb in ON]
        for _j, (kk, aa, bb) in enumerate(ON):
            if kk == base + 'a': ON[_j] = (kk, a, round(a + F1, 4))
            elif kk == base + 'b': ON[_j] = (kk, round(a + F1, 4), round(a + F2, 4))
            elif kk == base + 'c': ON[_j] = (kk, round(a + F2, 4), bb)
  # cards switch exactly on the cut frame
if V2:
    ON = [(k, a, b) for k, a, b in ON if not k.startswith(('BADGE', 'FBTN', 'MARK')) and (k in cards)]
    ON = [('GRAD', a, b) for k, a, b in ON if k.startswith(('T', 'RECAP'))] + ON  # gradient goes UNDER the text (was drawn on top and greyed the titles, 21.10)
    ON += [(kk, s0, s1) for kk, ch, s0, s1 in V2SUB]
else: ON += [(f'S{i:02d}', s0, s1) for i, (txt, s0, s1) in enumerate(clean)]
if S.get('logo'): ON.append(('LOGO', 0, T))
wh = [round(c - 0.22, 3) for c in cuts[1:-1]]
imp = [round(s['t0'] + s['shk'][0], 3) for s in segs if s.get('shk')]
pops = [round(cuts[i] + 0.05, 3) for i, l in enumerate(L)]
json.dump({'ON': ON, 'pos': pos, 'wh': wh, 'imp': imp, 'pops': pops, 'T': T}, open(f'{W}/ovplan.json', 'w'))
print('ovplan', len(ON))
