"""22.10: Hebrew voice takes with Chatterbox Multilingual (CPU, free), voice 3 timbre with intonation (Dima's pick he_A).
Lines are read in CHUNKS of 2-3 sentences (one sentence alone comes out slow and garbled: WER 0.6-0.9 on 22.10; the
casting sample Dima approved was one long read). cb_split.py then cuts the chunks into per-line files by whisper alignment.
Writes /s17/takes/<name>/C<c>_t<n>.wav and chunks.json. usage: python cb_takes.py <spec.json> <name> [takes=3]"""
import json, os, sys
import torch, torchaudio as ta, perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
SP, NAME = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 3
S = json.load(open(SP)); LINES = S.get('ref_lines', S['lines'])
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices', 'he_voice3_ref.wav')
O = f'/s17/takes/{NAME}'; os.makedirs(O, exist_ok=True)
MAXW, MAXL = S.get('cb', {}).get('chunk_words', 22), S.get('cb', {}).get('chunk_lines', 3)
chunks = []
for i, t in enumerate(LINES):
    if chunks and len(chunks[-1]) < MAXL and sum(len(LINES[j].split()) for j in chunks[-1]) + len(t.split()) <= MAXW: chunks[-1].append(i)
    else: chunks.append([i])
print('chunks', chunks, flush=True)
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
cb = S.get('cb', {}); ex, cfg = cb.get('exaggeration', 0.65), cb.get('cfg_weight', 0.4)
out = []
for c, idx in enumerate(chunks):
    text = ' '.join(LINES[i].strip() for i in idx)
    for n, seed in enumerate((7, 11, 23, 31, 47)[:N]):
        torch.manual_seed(seed)
        w = m.generate(text, language_id='he', audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg)
        f = f'{O}/C{c}_t{n}.wav'; ta.save(f, w, m.sr); out.append({'chunk': c, 'lines': idx, 'take': n, 'file': f, 'text': text, 'dur': round(w.shape[-1] / m.sr, 2)})
        print('take', c, n, round(w.shape[-1] / m.sr, 2), 's', flush=True)
json.dump(out, open(f'{O}/chunks.json', 'w'), ensure_ascii=False, indent=1); print('chunk takes', len(out))
