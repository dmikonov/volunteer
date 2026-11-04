import soundfile as sf, numpy as np, torch, json
torch.set_num_threads(2)
from kokoro import KPipeline
p = KPipeline(lang_code='a')
L = ['Nobody tells you this, but a lot of surfers freeze in the wrong wetsuit.', 'Pick it by water temperature, not by price.', 'Seventy-five and up? Boardshorts.', 'Sixty-eight to seventy-five? A spring suit.', 'Sixty to sixty-eight? A three-two.', 'Fifty-two to sixty? A four-three, plus booties.', 'Colder? Five-four, hood, gloves.', 'Save this.', "I'm your AI surf coach at SurfTribe.", 'Check the water, not the price.']
out = {}
for i, t in enumerate(L):
    auds, words, off = [], [], 0.0
    for r in p(t, voice='af_heart', speed=1.05):
        a = r.audio.numpy() if hasattr(r.audio, 'numpy') else np.asarray(r.audio)
        for tk in (r.tokens or []):
            if tk.start_ts is not None and tk.text.strip():
                words.append([tk.text, round(off + tk.start_ts, 3), round(off + (tk.end_ts or tk.start_ts), 3)])
        auds.append(a); off += len(a) / 24000
    sf.write(f'vo_{i}.wav', np.concatenate(auds), 24000)
    out[i] = {'text': t, 'dur': round(off, 3), 'words': words}
    print(i, round(off, 2), len(words), flush=True)
json.dump(out, open('words.json', 'w'), indent=1)
from huggingface_hub import HfApi
HfApi().upload_folder(folder_path='.', allow_patterns=['vo_*.wav', 'words.json'], path_in_repo='reels/voice_wetsuit', repo_id='dmikonov/surftribe-media', repo_type='dataset')
print('TTS_DONE')
