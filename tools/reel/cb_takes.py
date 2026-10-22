"""22.10: Hebrew voice takes with Chatterbox Multilingual (CPU, free), voice 3 timbre with intonation (Dima's pick he_A).
Writes /s17/takes/<name>/L<i>_t<n>.wav and fills "f5_takes" in the spec with file:// paths, so voice_f5.py picks the best
take per line by ivrit-ai whisper. usage: python cb_takes.py <spec.json> <name> [takes=3]"""
import json, os, sys
import torch, torchaudio as ta, perth
if perth.PerthImplicitWatermarker is None: perth.PerthImplicitWatermarker = perth.DummyWatermarker
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
SP, NAME = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 3
S = json.load(open(SP)); LINES = S.get('ref_lines', S['lines'])
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voices', 'he_voice3_ref.wav')
O = f'/s17/takes/{NAME}'; os.makedirs(O, exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
cb = S.get('cb', {}); ex, cfg = cb.get('exaggeration', 0.65), cb.get('cfg_weight', 0.4)
takes = []
for i, t in enumerate(LINES):
    for n, seed in enumerate((7, 11, 23, 31, 47)[:N]):
        torch.manual_seed(seed)
        w = m.generate(t, language_id='he', audio_prompt_path=REF, exaggeration=ex, cfg_weight=cfg)
        f = f'{O}/L{i + 1}_t{n}.wav'; ta.save(f, w, m.sr); takes.append([i, 'file://' + f]); print('take', i, n, flush=True)
S['f5_takes'] = takes; json.dump(S, open(SP, 'w'), ensure_ascii=False, indent=1)
print('takes', len(takes))
