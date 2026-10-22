"""Voice casting 22.10: expressive free TTS on the new knees script. Output: out/ci/voicecast2/*.mp3"""
import os, sys, time, subprocess as sp
import torch, torchaudio as ta
O = 'out/ci/voicecast2'; os.makedirs(O, exist_ok=True)
EN = ("This is why a tiny bump throws you off. Look at his knees. Locked straight. "
      "Straight legs send the bump into your body. Bent knees soak it up. "
      "Sit low, like there's a chair behind you. Film one wave. SurfTribe shows your knee angle. "
      "Tomorrow: how to spot a rip current from the beach.")
HE = ("בגלל זה גל קטן מפיל אתכם. תסתכלו על הברכיים. נעולות וישרות. "
      "רגל ישרה מעבירה כל קפיצה לגוף. ברך כפופה בולמת אותה. "
      "שבו נמוך, כאילו יש כיסא מאחוריכם. צלמו גל אחד, ובסרף טרייב תראו את זווית הברך. "
      "מחר: איך מזהים זרם סחף מהחוף.")
REF_EN, REF_HE = '/tmp/ref_en.wav', '/tmp/ref_he.wav'
def mp3(src, name):
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', 'loudnorm=I=-15:TP=-2', '-ar', '44100', '-b:a', '160k', f'{O}/{name}.mp3'], check=True)
    print('OK', name, flush=True)
def run(model, name, text, **kw):
    t = time.time()
    try:
        torch.manual_seed(kw.pop('seed', 7))
        wav = model.generate(text, **kw)
        ta.save(f'/tmp/{name}.wav', wav, model.sr); mp3(f'/tmp/{name}.wav', name)
        print(f'  {name}: {time.time() - t:.0f}s', flush=True)
    except Exception as e: print('FAIL', name, repr(e), flush=True)
which = sys.argv[1]
if which == 'en':
    from chatterbox.tts import ChatterboxTTS
    m = ChatterboxTTS.from_pretrained(device='cpu')
    run(m, 'en_A_chatterbox_default', EN, exaggeration=0.5, cfg_weight=0.5)
    run(m, 'en_B_chatterbox_lively', EN, exaggeration=0.75, cfg_weight=0.35)
    if os.path.exists(REF_EN): run(m, 'en_C_chatterbox_old_voice_lively', EN, audio_prompt_path=REF_EN, exaggeration=0.7, cfg_weight=0.4)
else:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    m = ChatterboxMultilingualTTS.from_pretrained(device='cpu')
    if os.path.exists(REF_HE): run(m, 'he_A_chatterbox_voice3_lively', HE, language_id='he', audio_prompt_path=REF_HE, exaggeration=0.65, cfg_weight=0.4)
    run(m, 'he_B_chatterbox_default', HE, language_id='he', exaggeration=0.6, cfg_weight=0.4)
