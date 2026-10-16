"""Run in the HF sandbox (network): word timestamps for live Hebrew speech -> subs JSON for reelkit.
pip install faster-whisper soundfile scipy imageio-ffmpeg ; python asr_he.py clip.mp4 out.json
Model ivrit-ai/whisper-large-v3-turbo-ct2 (Hebrew fine-tune). Chunks of max 3 words or 1.6 s per subtitle."""
import sys, json, subprocess, numpy as np, imageio_ffmpeg
from faster_whisper import WhisperModel
F = imageio_ffmpeg.get_ffmpeg_exe()
a = np.frombuffer(subprocess.run([F, '-v', 'error', '-i', sys.argv[1], '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
m = WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2', device='cpu', compute_type='int8')
segs, _ = m.transcribe(a, language='he', word_timestamps=True, vad_filter=True)
words = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
subs, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) == 3 or cur[-1][2] - cur[0][1] > 1.6 or w[0].endswith(('.', '?', ',')):
        subs.append({'text': ' '.join(x[0] for x in cur).rstrip('.'), 't0': round(cur[0][1], 2), 't1': round(cur[-1][2] + 0.1, 2)}); cur = []
if cur: subs.append({'text': ' '.join(x[0] for x in cur).rstrip('.'), 't0': round(cur[0][1], 2), 't1': round(cur[-1][2] + 0.1, 2)})
json.dump({'words': words, 'subs': subs}, open(sys.argv[2], 'w'), ensure_ascii=False, indent=1); print(len(words), 'words', len(subs), 'subs')
