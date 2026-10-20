#!/bin/bash
# EN voice casting: same text in 8 free voices -> out/ci/voicetest/*.mp3
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq espeak-ng ffmpeg > /dev/null
pip install -q edge-tts "kokoro>=0.9.4" soundfile > /dev/null 2>&1 || pip install edge-tts kokoro soundfile
mkdir -p out/ci/voicetest
python3 tools/reel/ci/voicetest.py
ls -la out/ci/voicetest
