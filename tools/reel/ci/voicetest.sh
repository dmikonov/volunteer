#!/bin/bash
# EN voice casting, part 2: Kokoro (needs Python 3.12, runner has 3.14) -> out/ci/voicetest/5-8_*.mp3
mkdir -p out/ci/voicetest; LOG=out/ci/voicetest/log_kokoro.txt
{
sudo apt-get update -qq && sudo apt-get install -y -qq espeak-ng ffmpeg > /dev/null && echo APT_OK
python3 -m pip install -q uv && echo UV_OK
uv run --python 3.12 --with "kokoro>=0.9.4" --with soundfile --with numpy --with "misaki[en]" python tools/reel/ci/voicetest_k.py
ls -la out/ci/voicetest
} > $LOG 2>&1
cat $LOG
