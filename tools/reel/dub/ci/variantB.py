"""CI pipeline for the Hebrew '5 things' reel, variant B (fast hook).
voice takes from the F5 Hebrew Space -> pick best per unit -> voice track -> music bed -> build_he.py -> out/
run from the repo root on a GitHub runner (see .github/workflows/reel-he.yml)."""
import json, os, re, sys, shutil, tarfile, csv, time, subprocess as sp
import numpy as np, soundfile as sf, librosa, editdistance

ROOT = os.getcwd(); W = '/s17/ci'; os.makedirs(f'{W}/t', exist_ok=True); os.makedirs(f'{ROOT}/out', exist_ok=True)
CFG = json.load(open(f'{ROOT}/tools/reel/dub/ci/voiceB.json'))
U, V = CFG['units'], CFG['voc']
SEEDS = CFG.get('seeds', list(range(8))); SPEEDS = CFG.get('speeds', [0.9, 1.0])
REF_ID = '12632262789732552882'
log = open(f'{ROOT}/out/beginners5_he_B_log.txt', 'w')
def say(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); log.write(s + '\n'); log.flush()

# ---------- reference voice (FLEURS he_il, voice 3) ----------
from huggingface_hub import hf_hub_download as d
tsv = d('google/fleurs', 'data/he_il/dev.tsv', repo_type='dataset')
REF_TXT = [r[2] for r in csv.reader(open(tsv), delimiter='\t') if len(r) >= 7 and r[1] == f'{REF_ID}.wav'][0]
REF = f'{W}/ref.wav'
with tarfile.open(d('google/fleurs', 'data/he_il/audio/dev.tar.gz', repo_type='dataset')) as tf:
    m = [x for x in tf.getmembers() if x.name.endswith(f'{REF_ID}.wav')][0]
    open(REF, 'wb').write(tf.extractfile(m).read())
say('ref', REF_TXT)

# ---------- takes ----------
TK = f'{ROOT}/tools/reel/dub/ci/takesB.json'   # takes made via the authenticated MCP tool: [[unit, speed, seed, url], ...]
if os.path.exists(TK):
    takes = []
    for i, spd, s, u in json.load(open(TK)):
        out = f'{W}/t/u{i}_{spd}_{s}.wav'
        r = sp.run(['curl', '-sfL', '-o', out, u])
        if r.returncode == 0 and os.path.getsize(out) > 1000: takes.append((i, spd, s, out))
        else: say('download failed', i, spd, s)
    SEEDS = []
from gradio_client import Client, handle_file
c = None
if not os.path.exists(TK):
  for k in range(10):
    try: c = Client('dmikonov/f5-hebrew', verbose=False); break
    except Exception as e: say('space not ready', str(e)[:120]); time.sleep(30)
  takes = []
for i, v in (enumerate(V) if not os.path.exists(TK) else []):
    for spd in SPEEDS:
        for s in SEEDS:
            out = f'{W}/t/u{i}_{spd}_{s}.wav'
            for attempt in range(3):
                try:
                    r = c.predict(handle_file(REF), REF_TXT, v, spd, 32, 2.0, s, api_name='/gen')
                    shutil.copy(r, out); takes.append((i, spd, s, out)); break
                except Exception as e:
                    say('gen retry', i, spd, s, str(e)[:150]); time.sleep(20)
say('takes', len(takes))

# ---------- evaluate ----------
from faster_whisper import WhisperModel
wm = WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2', device='cpu', compute_type='int8', cpu_threads=4)
norm = lambda s: re.sub('[^א-ת0-9 ]', '', s).split()
def ld(f, sr=16000):
    return np.frombuffer(sp.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
NUM = {'1': 'אחת', '2': 'שתיים', '3': 'שלוש', '4': 'ארבע', '5': 'חמש', '10': 'עשר'}
def words_norm(ws):
    out = []
    for w in ws:
        w = re.sub('[^א-ת0-9]', '', w)
        if w in NUM: w = NUM[w]
        if w: out.append(w)
    return out
ev = []
for i, spd, s, f in takes:
    a = ld(f)
    seg, _ = wm.transcribe(a, language='he', beam_size=2, word_timestamps=True)
    Wd = [(w.word.strip(), w.start, w.end) for sg in seg for w in sg.words]
    hyp = words_norm([w[0] for w in Wd]); ref = words_norm(U[i].split())
    wer = editdistance.eval(ref, hyp) / len(ref)
    f0, vv, _ = librosa.pyin(a, fmin=60, fmax=300, sr=16000, frame_length=1024); f0 = f0[vv]
    med = float(np.median(f0)) if len(f0) > 10 else 0.0
    rng = float(np.percentile(12 * np.log2(f0 / med), 95) - np.percentile(12 * np.log2(f0 / med), 5)) if med else 0.0
    ev.append({'i': i, 'spd': spd, 's': s, 'f': f, 'wer': round(wer, 3), 'med': round(med), 'rng': round(rng, 1), 'dur': round(len(a) / 16000, 2), 'w': Wd, 'txt': ' '.join(w[0] for w in Wd)})
    say('eval', i, spd, s, ev[-1]['wer'], ev[-1]['med'], ev[-1]['rng'], ev[-1]['txt'])

TARGET = CFG.get('pitch_target', 130)
picks = []
for i in range(len(U)):
    cand = [e for e in ev if e['i'] == i and e['med'] > 0]
    best_wer = min(e['wer'] for e in cand)
    ok = [e for e in cand if e['wer'] <= best_wer + 1e-9]
    ok.sort(key=lambda e: (abs(np.log2(e['med'] / TARGET)), -e['rng']))
    picks.append(ok[0]); say('PICK', i, ok[0]['spd'], ok[0]['s'], 'wer', ok[0]['wer'], 'med', ok[0]['med'], ok[0]['txt'])
json.dump([{k: v for k, v in p.items() if k != 'w'} | {'w': p['w']} for p in picks], open(f'{ROOT}/out/beginners5_he_B_picks.json', 'w'), ensure_ascii=False, indent=1)

# ---------- voice track ----------
GAP = [0.0] + [0.34] * (len(picks) - 1)
out, words, t = [], [], 0.12
sr0 = sf.info(picks[0]['f']).samplerate; out.append(np.zeros(int(0.12 * sr0)))
for k, p in enumerate(picks):
    a, sr = sf.read(p['f']); a = a if a.ndim == 1 else a.mean(1); assert sr == sr0
    env = np.sqrt(np.convolve(a ** 2, np.ones(240) / 240, 'same')); idx = np.where(env > 0.01 * np.abs(a).max())[0]
    s0 = max(0, idx[0] / sr - 0.03); e0 = min(len(a) / sr, idx[-1] / sr + 0.15)
    if k: out.append(np.zeros(int(GAP[k] * sr))); t += GAP[k]
    seg = a[int(s0 * sr):int(e0 * sr)].copy(); fd = int(0.012 * sr); seg[:fd] *= np.linspace(0, 1, fd); seg[-fd:] *= np.linspace(1, 0, fd)
    out.append(seg)
    for j, (w, ws, we) in enumerate(p['w']):
        words.append([w, round(t if j == 0 else max(t, t + ws - s0), 3), round(t + we - s0, 3), k])
    t += e0 - s0
y = np.concatenate(out); sf.write(f'{W}/voB.wav', y, sr0)
json.dump(words, open(f'{W}/voB.words.json', 'w'), ensure_ascii=False)
say('voice', round(len(y) / sr0, 2), 's')

def find(u, alts, nth=0):
    hits = [n for n, w in enumerate(words) if w[3] == u and any(re.sub('[^א-ת0-9]', '', w[0]).startswith(a) for a in alts)]
    if not hits: raise SystemExit(f'anchor not found: unit {u} {alts}')
    return hits[nth]
first = lambda u: [n for n, w in enumerate(words) if w[3] == u][0]

# ---------- music bed (EN reel minus voice) ----------
url = open(f'{ROOT}/tools/reel/dub/ci/en_url.txt').read().strip()
sp.run(['curl', '-sL', '-o', f'{W}/en.mp4', url], check=True)
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/en.mp4', '-vn', '-ac', '2', '-ar', '44100', f'{W}/en.wav'], check=True)
sp.run([sys.executable, '-m', 'demucs', '--two-stems=vocals', '-n', 'htdemucs', '-o', f'{W}/sep', f'{W}/en.wav'], check=True)
MUSIC = f'{W}/sep/htdemucs/en/no_vocals.wav'

# ---------- stock (Coverr / Mixkit, free licence) ----------
H = f'{W}/hd/'; os.makedirs(H, exist_ok=True)
SRC = {'1127': 'https://assets.mixkit.co/videos/1127/1127-1080.mp4', '1032': 'https://assets.mixkit.co/videos/1032/1032-1080.mp4',
       'pier': 'https://cdn.coverr.co/videos/coverr-serene-surfer-gazing-at-the-sea/1080p.mp4', 'white': 'https://cdn.coverr.co/videos/coverr-surfer-catching-a-wave-5342/1080p.mp4',
       'wax': 'https://cdn.coverr.co/videos/coverr-a-man-waxing-a-surfboard-359/1080p.mp4', 'leash': 'https://cdn.coverr.co/videos/coverr-surfer-walks-towards-waves/1080p.mp4',
       'sea': 'https://cdn.coverr.co/videos/coverr-a-female-surfer-waiting-for-a-wave-8785/1080p.mp4', 'man': 'https://cdn.coverr.co/videos/coverr-guy-surfing-in-the-sea-9468/1080p.mp4'}
for k, u in SRC.items():
    sp.run(['curl', '-sL', '-A', 'Mozilla', '-o', f'{H}{k}.mp4', u], check=True)

spec = {
    'out': f'{W}/rb', 'vo': f'{W}/voB.wav', 'words_file': f'{W}/voB.words.json', 'music': MUSIC, 'music_gain_db': 10.5, 'tail': 0.6, 'mark': 0,
    'end_at': find(3, ['שמרו']),
    'shots': [
        {'key': 'hook', 'at': 0, 'src': H + '1127.mp4', 'ss': 10.6, 'x': 0.57},
        {'key': 'walk', 'at': find(0, ['קודם']), 'src': H + '1032.mp4', 'ss': 15.2, 'x': 0.51},
        {'key': 'pier', 'at': first(1), 'src': H + 'pier.mp4', 'ss': 2.3, 'x': 0.6},
        {'key': 'white', 'at': find(1, ['שתיים', '2']), 'src': H + 'white.mp4', 'ss': 9.2, 'x': 0.51},
        {'key': 'wax', 'at': first(2), 'src': H + 'wax.mp4', 'ss': 3.2, 'x': 0.88},
        {'key': 'leash', 'at': find(2, ['ארבע', '4']), 'src': H + 'leash.mp4', 'ss': 1.8, 'x': 0.55},
        {'key': 'sea', 'at': first(3), 'src': H + 'sea.mp4', 'ss': 0.0, 'x': 0.45},
        {'key': 'man', 'at': find(3, ['ואז']), 'src': H + 'man.mp4', 'ss': 1.2, 'x': 0.42},
        {'key': 'end', 'at': find(3, ['שמרו']), 'src': H + 'man.mp4', 'ss': 'cont', 'x': 0.42}],
    'titles': [
        {'shot': 'hook', 'hook': True, 'l1': 'רגע!', 'l2': 'אל תחתרו עדיין'},
        {'shot': 'walk', 'hook': True, 'l1': 'קודם', 'l2': '5 דברים'},
        {'shot': 'pier', 'n': 1, 'l1': 'עשר דקות<br>על הסטים'},
        {'shot': 'white', 'n': 2, 'l1': 'מתחילים<br>בקצף'},
        {'shot': 'wax', 'n': 3, 'l1': 'שעווה<br>לגלשן'},
        {'shot': 'leash', 'n': 4, 'l1': 'בודקים<br>את הליש'},
        {'shot': 'sea', 'n': 5, 'l1': 'נקודת ציון<br>על החוף'},
        {'shot': 'man', 'l1': 'מצלמים', 'l2': 'ומקבלים תיקון אחד'}],
    'subs': [[find(3, ['וסרף', 'ושרף', 'סרף']), 'וסרף טרייב מראה לכם'], [find(3, ['מה']), 'מה לתקן']],
}
json.dump(spec, open(f'{W}/spec.json', 'w'), ensure_ascii=False, indent=1)
sp.run([sys.executable, f'{ROOT}/tools/reel/dub/build_he.py', f'{W}/spec.json'], check=True)

# ---------- outputs ----------
R = f'{W}/rb/reel.mp4'
shutil.copy(R, f'{ROOT}/out/reel_beginners5_he_B.mp4')
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', R, '-vf', 'fps=2,scale=180:320,tile=10x4', '-frames:v', '1', '-q:v', '5', f'{ROOT}/out/beginners5_he_B_sheet.jpg'], check=True)
say('DONE', sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', R], capture_output=True, text=True).stdout.strip())
