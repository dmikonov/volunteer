"""TTS + trimmed voice track. usage: python3 voice.py <workdir>  (spec.json: lang, lines[])"""
import asyncio, json, sys, subprocess as sp, edge_tts
W = sys.argv[1]; S = json.load(open(f'{W}/spec.json')); LANG = S['lang']; SR = 48000; GAP = S.get('gap', 0.34)
VO = {'he': ('he-IL-AvriNeural', '+18%'), 'en': ('en-US-AndrewNeural', '+8%')}
def dur(f):
    r = sp.run(['ffmpeg', '-hide_banner', '-i', f], capture_output=True, text=True).stderr
    h, m, s = r.split('Duration: ')[1].split(',')[0].split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
async def tts():
    v, r = VO[LANG]; r = S.get('rate', r); out = []
    for i, t in enumerate(S['lines'], 1):
        try: c = edge_tts.Communicate(t, v, rate=r, boundary='WordBoundary')
        except TypeError: c = edge_tts.Communicate(t, v, rate=r)
        audio = bytearray(); words = []
        async for ch in c.stream():
            if ch['type'] == 'audio': audio += ch['data']
            elif ch['type'] == 'WordBoundary': words.append([ch['text'], ch['offset'] / 1e7, (ch['offset'] + ch['duration']) / 1e7])
        fn = f'{W}/L{i}.mp3'; open(fn, 'wb').write(audio)
        out.append({'k': f'L{i}', 'txt': t, 'fn': fn, 'words': words})
    return out
def kokoro(cfg):
    import shutil, os
    if not shutil.which('uv'): sp.run([sys.executable, '-m', 'pip', 'install', '-q', 'uv'], check=True)
    if not shutil.which('espeak-ng'): sp.run('sudo apt-get install -y -qq espeak-ng > /dev/null 2>&1 || apt-get install -y -qq espeak-ng > /dev/null 2>&1', shell=True)
    here = os.path.dirname(os.path.abspath(__file__))
    sp.run(['uv', 'run', '--python', '3.12', '--with', 'kokoro>=0.9.4', '--with', 'soundfile', '--with', 'numpy', '--with', 'misaki[en]',
            'python', f'{here}/kokoro_tts.py', W, cfg['voice'], str(S.get('kokoro_speed', cfg.get('speed', 1.0)))], check=True)
    return json.load(open(f'{W}/kokoro.json'))
import os
_cfgf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices.json')
CFG = json.load(open(_cfgf)) if os.path.exists(_cfgf) else {}
L = None
if LANG == 'en' and CFG.get('en', {}).get('engine') == 'kokoro' and not S.get('edge'):
    try: L = kokoro(CFG['en']); print('voice: kokoro', CFG['en']['voice'])
    except Exception as e: print('KOKORO FAIL, fallback edge:', e)
if L is None:
    if LANG == 'en' and CFG.get('en_fallback'): VO['en'] = (CFG['en_fallback']['voice'], CFG['en_fallback'].get('rate', '+5%'))
    L = asyncio.run(tts())
t = 0.12
for l in L:
    s0 = max(0.0, l['words'][0][1] - 0.04); e0 = min(dur(l['fn']), l['words'][-1][2] + 0.10)
    l['s0'], l['e0'] = s0, e0; l['t0'] = round(t, 3); l['d'] = e0 - s0
    l['words'] = [[w, t + a - s0, t + b - s0] for w, a, b in l['words']]; t += l['d'] + GAP + S.get('gap_after', {}).get(l['k'], 0)  # 22.10 Dima: a breath after the follow line and before a new point
T = round(L[-1]['t0'] + L[-1]['d'] + 0.9, 3)
inputs, fc, seq, cur = [], [], [], 0.0
for i, l in enumerate(L):
    sil = l['t0'] - cur
    if sil > 0.001: fc.append(f'aevalsrc=0:d={sil:.3f}:s={SR}:c=mono[s{i}]'); seq.append(f'[s{i}]')
    inputs += ['-i', l['fn']]; fc.append(f"[{len(inputs) // 2 - 1}:a]atrim=start={l['s0']:.3f}:end={l['e0']:.3f},asetpts=PTS-STARTPTS,aresample={SR},aformat=channel_layouts=mono[a{i}]"); seq.append(f'[a{i}]')
    cur = l['t0'] + l['d']
fc.append(f"{''.join(seq)}concat=n={len(seq)}:v=0:a=1,apad=whole_dur={T}[vo]")
sp.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', ';'.join(fc), '-map', '[vo]', '-t', str(T), f'{W}/vo_raw.wav'], check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{W}/vo_raw.wav', '-af', 'loudnorm=I=-15:TP=-2:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ln = f"loudnorm=I=-15:TP=-2:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/vo_raw.wav', '-af', ln, '-ar', '48000', '-ac', '2', f'{W}/vo.wav'], check=True)
json.dump({'T': T, 'L': L}, open(f'{W}/tl.json', 'w'), ensure_ascii=False)
print(LANG, 'T', T, [(l['k'], l['t0'], round(l['d'], 2)) for l in L])
