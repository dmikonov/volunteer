# 20.10 foam reel (23.10): full build on GitHub Actions (HF sandbox 402)
set -x
R=$PWD; O=$R/out/ci/foam
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
pip install -q edge-tts opencv-python-headless numpy playwright
python -m playwright install --with-deps chromium >/dev/null 2>&1
sudo mkdir -p /s17 && sudo chown $USER /s17 && mkdir -p /s17/gen /s17/rp /s17/tip1
cp appkit/Rubik.ttf /s17/Rubik.ttf; cp $O/gen/f_*.mp4 /s17/gen/
python3 tools/reel/ci/app_panel.py app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 10.6 11.6 760 900 1480 1615 7 /s17/gen/app_he.mp4
python3 tools/reel/ci/app_panel.py app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 21.8 22.6 900 900 1620 1750 7 /s17/gen/app_en.mp4
python3 tools/reel/audio_fx.py 30
cd /s17/rp && for f in voice.py build.py ov_png.py ov_ff.py trim_tail.py post_cz.py; do cp $R/tools/reel/$f .; done
for k in foam_he foam_en; do mkdir -p $k && cp $R/tools/reel/specs/$k.json $k/spec.json; done
run(){ k=$1; python3 voice.py $k && python3 build.py $k && python3 ov_png.py $k && python3 ov_ff.py $k && python3 trim_tail.py $k && python3 post_cz.py $k; echo "EXIT $k $?"; }
run foam_he > foam_he/log.txt 2>&1 &
run foam_en > foam_en/log.txt 2>&1 &
wait
for k in foam_he foam_en; do
  D=$O/$k; mkdir -p $D/ov $D/fr; cp $k/log.txt $k/tl.json $k/ovplan.json $k/sheet.jpg $k/prev.mp4 $D/ 2>/dev/null; cp $k/reel_*.mp4 $D/ 2>/dev/null; cp $k/ov/*.png $D/ov/ 2>/dev/null; cp $k/vo.wav $D/ 2>/dev/null
  F=$(ls $k/reel_*.mp4); ffprobe -v error -show_entries format=duration -of csv=p=0 $F > $D/dur.txt
  ffmpeg -hide_banner -i $F -af ebur128=peak=true -f null - 2>&1 | tail -12 > $D/loud.txt
  ffmpeg -hide_banner -i $k/vo_raw.wav -af silencedetect=n=-40dB:d=0.3 -f null - 2>&1 | grep silence_ > $D/gaps.txt
  ffmpeg -v error -y -i $F -vf "fps=10,scale=216:384,drawtext=text='%{pts\:hms}':x=4:y=360:fontsize=16:fontcolor=yellow,tile=8x5" $D/fr/f10_%02d.jpg
  for t in 0.5 3 6 9 12 15 18; do ffmpeg -v error -y -ss $t -i $F -frames:v 1 $D/fr/full_$t.jpg; done
done
