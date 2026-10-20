# 21.10 generic reel build on GitHub Actions. Names in tools/reel/ci/NAMES (one per line, = spec name in tools/reel/specs).
# Clips: every out/ci/*/gen/*.mp4 is copied to /s17/gen. Optional per-reel prep: tools/reel/specs/<name>.prep.sh (app panels etc).
# HE spec with "f5": true -> voice via tools/reel/voice_f5.py (F5 voice 3), else voice.py (EN: Kokoro af_heart).
set -x
R=$PWD
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg espeak-ng >/dev/null
pip install -q edge-tts opencv-python-headless numpy playwright faster-whisper gradio_client soundfile librosa editdistance huggingface_hub
python -m playwright install --with-deps chromium >/dev/null 2>&1
sudo mkdir -p /s17 && sudo chown $USER /s17 && mkdir -p /s17/gen /s17/rp /s17/tip1 /s17/app
cp appkit/Rubik.ttf /s17/Rubik.ttf; cp out/ci/*/gen/*.mp4 /s17/gen/ 2>/dev/null; cp app-screens/*.mp4 /s17/app/ 2>/dev/null
NAMES=$(grep -v '^#' tools/reel/ci/NAMES)
for k in $NAMES; do [ -f tools/reel/specs/$k.prep.sh ] && bash tools/reel/specs/$k.prep.sh; done
N1=$(echo $NAMES | wc -w); [ "$N1" = 1 ] && [ -f tools/reel/specs/$NAMES.music ] && export REEL_MUSIC=$(cat tools/reel/specs/$NAMES.music)  # 21.10: neighbour reels get different tracks
python3 tools/reel/audio_fx.py 30 | tee /s17/music.log
cd /s17/rp && for f in voice.py voice_f5.py build.py ov_png.py ov_ff.py trim_tail.py post_cz.py voicecheck.py kokoro_tts.py voices.json; do cp $R/tools/reel/$f . 2>/dev/null; done
for k in $NAMES; do mkdir -p $k && cp $R/tools/reel/specs/$k.json $k/spec.json; done
for k in $NAMES; do
  V=voice.py; grep -q '"f5": *true' $k/spec.json && V=voice_f5.py
  for i in 1 2 3 4; do python3 $V /s17/rp/$k > /s17/rp/$k/voice.log 2>&1 && break; sleep 8; done; tail -3 /s17/rp/$k/voice.log
  python3 voicecheck.py /s17/rp/$k > /s17/rp/$k/voicecheck.txt 2>&1
done
run(){ k=/s17/rp/$1; python3 build.py $k && python3 ov_png.py $k && python3 ov_ff.py $k && python3 trim_tail.py $k && python3 $R/tools/reel/loudfix.py $k/$(python3 -c "import json;print(json.load(open('$k/spec.json'))['out'])") && python3 post_cz.py $k; echo "EXIT $k $?"; }
for k in $NAMES; do run $k > /s17/rp/$k/log.txt 2>&1 & done
wait
for k in $NAMES; do
  D=$R/out/ci/$k; mkdir -p $D/ov $D/fr; cp /s17/music.log $k/voice.log $k/voicecheck.txt $k/log.txt $k/tl.json $k/ovplan.json $k/sheet.jpg $k/prev.mp4 $D/ 2>/dev/null; cp $k/reel_*.mp4 $D/ 2>/dev/null; cp $k/ov/*.png $D/ov/ 2>/dev/null; cp $k/vo.wav $D/ 2>/dev/null
  F=$(ls /s17/rp/$k/reel_*.mp4 | head -1); [ -z "$F" ] && continue; ffprobe -v error -show_entries format=duration -of csv=p=0 $F > $D/dur.txt
  ffmpeg -hide_banner -i $F -af ebur128=peak=true -f null - 2>&1 | tail -12 > $D/loud.txt
  ffmpeg -hide_banner -i $k/vo_raw.wav -af silencedetect=n=-40dB:d=0.3 -f null - 2>&1 | grep silence_ > $D/gaps.txt
  ffmpeg -v error -y -i $F -vf "fps=10,scale=216:384,drawtext=text='%{pts\:hms}':x=4:y=360:fontsize=16:fontcolor=yellow,tile=8x5" $D/fr/f10_%02d.jpg
  for t in 0.5 1.5 2.5 3.5 6 9 12 15 18; do ffmpeg -v error -y -ss $t -i $F -frames:v 1 -q:v 3 $D/fr/full_$t.jpg; done
done
