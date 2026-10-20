import asyncio, subprocess as sp, edge_tts, numpy as np, soundfile as sf
T = ("Stop looking at your feet. Follow, I fix one surf mistake a day. "
     "Eyes down, you stall. Eyes ahead, you keep riding. "
     "Chin up, look along the wave, and the board follows.")
O = 'out/ci/voicetest'
def mp3(src, name):
    sp.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', 'loudnorm=I=-15:TP=-2', '-ar', '44100', '-b:a', '160k', f'{O}/{name}.mp3'], check=True)
edge = {'1_edge_andrew_current': ('en-US-AndrewNeural', '+8%'), '2_edge_andrew_multi': ('en-US-AndrewMultilingualNeural', '+5%'),
        '3_edge_brian_multi': ('en-US-BrianMultilingualNeural', '+5%'), '4_edge_ava_multi': ('en-US-AvaMultilingualNeural', '+5%')}
async def run_edge():
    for n, (v, r) in edge.items():
        try:
            await edge_tts.Communicate(T, v, rate=r).save(f'/tmp/{n}.mp3'); mp3(f'/tmp/{n}.mp3', n)
        except Exception as e: print('EDGE FAIL', n, e)
asyncio.run(run_edge())
try:
    from kokoro import KPipeline
    for lang, voices in (('a', ['af_heart', 'af_bella', 'am_michael', 'am_puck']),):
        p = KPipeline(lang_code=lang)
        for i, v in enumerate(voices, 5):
            a = np.concatenate([np.asarray(x[2]) for x in p(T, voice=v, speed=1.08)])
            sf.write(f'/tmp/k_{v}.wav', a, 24000); mp3(f'/tmp/k_{v}.wav', f'{i}_kokoro_{v}')
except Exception as e: print('KOKORO FAIL', e)
