#!/bin/bash
# check voice.py with Kokoro af_heart on a real EN spec -> out/ci/kokorotest/{vo.mp3,tl.json,log.txt}
mkdir -p out/ci/kokorotest /tmp/kt; LOG=out/ci/kokorotest/log.txt
{
sudo apt-get update -qq && sudo apt-get install -y -qq espeak-ng ffmpeg > /dev/null
python3 -m pip install -q edge-tts
python3 -c "import json;s=json.load(open('tools/reel/specs/look2_en.json'));json.dump({'lang':'en','lines':['Stop looking at your feet.','Follow, I fix one surf mistake a day.']+s['lines'][1:]},open('/tmp/kt/spec.json','w'))"
python3 tools/reel/voice.py /tmp/kt
ffmpeg -v error -y -i /tmp/kt/vo.wav -b:a 160k out/ci/kokorotest/vo.mp3
cp /tmp/kt/tl.json out/ci/kokorotest/
} > $LOG 2>&1
cat $LOG
