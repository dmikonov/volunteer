# 29.10 drop-in (whose wave): real stock only. Mixkit free licence (1074 aerial: rider + surfer in his path; 1127/1128 same session: rider at the peak, surfer on the shoulder; 1075 aerial ride), Pexels 856422 (crowded lineup).
[ -f /s17/gen/di_hook.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 1074 1127 1128 1075; do [ -s /tmp/px/m$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-1080.mp4; done
u2=$(grep "^7938440 " out/ci/d29/review/resolved.txt | cut -d' ' -f2); [ -s /tmp/px/p7938440.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p7938440.mp4 "$u2"
u=$(grep "^856422 " out/ci/d29/review/resolved.txt | cut -d' ' -f2); [ -s /tmp/px/p856422.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p856422.mp4 "$u"
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m1074 0.0 3.0 0.35 0.29 di_hook
cut m1074 3.0 3.0 0.27 0.40 di_pass
cut p856422 0.0 3.2 0.62 0.60 di_crowd
cut m1127 0.0 2.6 0.28 0.33 di_bridge
cut m1128 0.0 2.8 0.13 0.38 di_peak
cut m1128 0.0 2.6 0.86 0.86 di_look
cut m1128 1.5 1.8 0.86 0.86 di_wait
cut p7938440 8.55 2.33 0.55 0.55 di_hit
cut p856422 3.0 3.8 0.60 0.60 di_lineup
cut m1127 3.0 3.2 0.45 0.55 di_send2
cut m1128 4.8 3.4 0.52 0.62 di_ride
cut m1075 10.0 3.2 0.45 0.55 di_send
cut m1127 7.5 3.2 0.52 0.58 di_tmrw
# app: Ride Replay, real recordings (EN 12.10 at 45 s, HE 28.09 15:24 at 17 s), phone screen full bleed under the header
ffmpeg -v error -y -ss 45.0 -t 3.6 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/di_app_en.mp4
ffmpeg -v error -y -ss 17.6 -t 3.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/di_app_he.mp4
mkdir -p out/ci/d29/review; for f in $G/di_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=14x1" -frames:v 1 out/ci/d29/review/cut_$n.jpg; done
ls -la $G/di_*
