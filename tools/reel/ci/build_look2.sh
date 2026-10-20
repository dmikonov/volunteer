# 20.10 look reel v2 (after the trial post-mortem): GitHub Actions build, same pipeline as foam
set -x
R=$PWD; O=$R/out/ci/look2
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
pip install -q edge-tts opencv-python-headless numpy playwright
python -m playwright install --with-deps chromium >/dev/null 2>&1
sudo mkdir -p /s17 && sudo chown $USER /s17 && mkdir -p /s17/gen /s17/rp /s17/tip1
cp appkit/Rubik.ttf /s17/Rubik.ttf; cp assets/look2/g_*.mp4 /s17/gen/
# split screens (real time): eyes down = g_nose (board stalls), eyes ahead = g_along. HE reads right to left: "down" on the right
sp(){ ffmpeg -v error -y -ss 0.3 -i /s17/gen/$1 -ss 0.3 -i /s17/gen/$2 -filter_complex \
 "[0:v]crop=234:832:(iw-234)*$3:0,scale=537:1920:flags=lanczos,fps=25,setsar=1[l];[1:v]crop=234:832:(iw-234)*$4:0,scale=537:1920:flags=lanczos,fps=25,setsar=1[r];color=white:s=6x1920:r=25[d];[l][d][r]hstack=3,trim=duration=2.0,format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 14 /s17/gen/$5; }
sp g_nose.mp4 g_along.mp4 0.45 0.47 l_split_en.mp4
sp g_along.mp4 g_nose.mp4 0.47 0.45 l_split_he.mp4
python3 tools/reel/ci/app_panel.py app-screens/ScreenRecording_09-28-2026_10-56-35_1_2.mp4 27.3 29.9 760 480 1030 1240 3.2 /s17/gen/app_he.mp4 20 1040 760
python3 tools/reel/ci/app_panel.py app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 6.0 8.8 300 600 330 900 3.2 /s17/gen/app_en.mp4 0 1080 760
python3 tools/reel/audio_fx.py 30
cd /s17/rp && for f in voice.py build.py ov_png.py ov_ff.py trim_tail.py post_cz.py; do cp $R/tools/reel/$f .; done
for k in look2_he look2_en; do mkdir -p $k && cp $R/tools/reel/specs/$k.json $k/spec.json; done
for k in look2_he look2_en; do for i in 1 2 3 4; do python3 voice.py /s17/rp/$k > /s17/rp/$k/voice.log 2>&1 && break; sleep 8; done; tail -2 /s17/rp/$k/voice.log; done
run(){ k=/s17/rp/$1; python3 build.py $k && python3 ov_png.py $k && python3 ov_ff.py $k && python3 trim_tail.py $k && python3 $R/tools/reel/loudfix.py $k/$(python3 -c "import json;print(json.load(open('$k/spec.json'))['out'])") && python3 post_cz.py $k; echo "EXIT $k $?"; }
run look2_he > /s17/rp/look2_he/log.txt 2>&1 &
run look2_en > /s17/rp/look2_en/log.txt 2>&1 &
wait
for k in look2_he look2_en; do
  D=$O/$k; mkdir -p $D/ov $D/fr; cp $k/voice.log $k/log.txt $k/tl.json $k/ovplan.json $k/sheet.jpg $k/prev.mp4 $D/ 2>/dev/null; cp $k/reel_*.mp4 $D/ 2>/dev/null; cp $k/ov/*.png $D/ov/ 2>/dev/null
  F=$(ls /s17/rp/$k/reel_*.mp4 | head -1); [ -z "$F" ] && continue; ffprobe -v error -show_entries format=duration -of csv=p=0 $F > $D/dur.txt
  ffmpeg -hide_banner -i $F -af ebur128=peak=true -f null - 2>&1 | tail -12 > $D/loud.txt
  ffmpeg -hide_banner -i $k/vo_raw.wav -af silencedetect=n=-40dB:d=0.3 -f null - 2>&1 | grep silence_ > $D/gaps.txt
  ffmpeg -v error -y -i $F -vf "fps=10,scale=216:384,drawtext=text='%{pts\:hms}':x=4:y=360:fontsize=16:fontcolor=yellow,tile=8x5" $D/fr/f10_%02d.jpg
  for t in 0.5 2 4 6 9 12 15 18; do ffmpeg -v error -y -ss $t -i $F -frames:v 1 $D/fr/full_$t.jpg; done
done
