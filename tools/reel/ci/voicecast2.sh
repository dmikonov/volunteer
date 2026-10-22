#!/bin/bash
# Voice casting 22.10 (Chatterbox, CPU, free) + Edge multilingual baseline -> out/ci/voicecast2/
mkdir -p out/ci/voicecast2; LOG=out/ci/voicecast2/log.txt
{
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg > /dev/null && echo APT_OK
ffmpeg -v error -y -i out/ci/knees_bump_en/vo.wav -t 9 -ac 1 -ar 24000 /tmp/ref_en.wav && echo REF_EN
ffmpeg -v error -y -i out/ci/knees_bump_he/vo.wav -t 9 -ac 1 -ar 24000 /tmp/ref_he.wav && echo REF_HE
python3 -m pip install -q uv edge-tts && echo UV_OK
python3 - <<'EOF'
import asyncio, subprocess as sp, edge_tts
EN = ("This is why a tiny bump throws you off. Look at his knees. Locked straight. "
      "Straight legs send the bump into your body. Bent knees soak it up. "
      "Sit low, like there's a chair behind you. Film one wave. SurfTribe shows your knee angle. "
      "Tomorrow: how to spot a rip current from the beach.")
async def go():
    for n, v in (('en_D_edge_andrew_multi', 'en-US-AndrewMultilingualNeural'), ('en_E_edge_brian_multi', 'en-US-BrianMultilingualNeural')):
        try:
            await edge_tts.Communicate(EN, v, rate='+4%').save(f'/tmp/{n}.mp3')
            sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'/tmp/{n}.mp3', '-af', 'loudnorm=I=-15:TP=-2', '-ar', '44100', '-b:a', '160k', f'out/ci/voicecast2/{n}.mp3'], check=True); print('OK', n)
        except Exception as e: print('EDGE FAIL', n, e)
asyncio.run(go())
EOF
UVA="--python 3.11 --index-strategy unsafe-best-match --extra-index-url https://download.pytorch.org/whl/cpu --with chatterbox-tts>=0.1.4"
for L in he en; do
  timeout 1500 uv run $UVA python tools/reel/ci/voicecast2.py $L || echo "CHATTERBOX $L exit $?"
done
ls -la out/ci/voicecast2
} > $LOG 2>&1
cat $LOG
