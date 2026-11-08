# 09.11 night: 12.11 "last wave" (Ф13). Real Mixkit/Pexels (free licence): tired paddler Kampus 7938443, 7938445, whitewater 1076/1075/1127, exit man 7938104/106.
G=/s17/gen; S=out/ci/d09/src; R=out/ci/d09/review; mkdir -p $G $R
[ -f $G/lw_tmrw.mp4 ] && exit 0
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut p7938443 3.0 3.2 0.56 0.48 lw_hook
cut p7938432 1.0 3.6 0.40 0.45 lw_tired
cut m1076 3.0 3.2 0.42 0.52 lw_bridge
cut m1042 1.5 3.4 0.48 0.52 lw_late
cut m1127 19.2 3.2 0.55 0.60 lw_rise
cut m1127 15.0 2.6 0.52 0.58 lw_small
cut p7938104 4.0 4.2 0.44 0.52 lw_out
cut p7938106 0.5 4.0 0.40 0.45 lw_save
cut m1127 7.5 3.4 0.50 0.58 lw_tmrw
ffmpeg -v error -y -ss 17.0 -t 3.6 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/lw_app_en.mp4
ffmpeg -v error -y -ss 17.6 -t 3.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/lw_app_he.mp4
for f in $G/lw_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
