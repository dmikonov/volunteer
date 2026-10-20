#!/bin/bash
# EN voice casting: same text in 8 free voices -> out/ci/voicetest/*.mp3 (+ log.txt)
mkdir -p out/ci/voicetest; LOG=out/ci/voicetest/log.txt
{
python3 --version
sudo apt-get update -qq && sudo apt-get install -y -qq espeak-ng ffmpeg > /dev/null && echo APT_OK
python3 -m pip install -q edge-tts soundfile numpy && echo EDGE_OK
python3 -m pip install -q "kokoro>=0.9.4" && echo KOKORO_OK
python3 tools/reel/ci/voicetest.py
ls -la out/ci/voicetest
} > $LOG 2>&1
cat $LOG
