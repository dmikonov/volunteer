# 30.10 film a friend (HE): real stock + one Wan clip (the man filming at the water's edge, Z-Image seed 301030).
# Pexels 4782364 (Waikiki wide, surfers small) and 4782485 (same session, a ride) by Taryn Elliott, free licence; Mixkit 15845, 1069, 1220 free licence.
[ -f /s17/gen/fm_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 4782364 4782485; do [ -s /tmp/px/p$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p$id.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_30fps.mp4; done
for id in 15845; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6; sp=${7:-1}
  ffmpeg -v error -y -ss $ss -t $(awk "BEGIN{print $t*$sp}") -i /tmp/px/$src.mp4 -vf "setpts=PTS/$sp,scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut p4782364 1.0 7.0 0.45 0.45 fm_hook
cut p4782485 0.0 5.0 0.76 0.70 fm_ride
cut m15845 0.0 9.8 0.56 0.56 fm_long 2
ffmpeg -v error -y -i out/ci/d30/gen/fm_board_raw.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/fm_board.mp4
ffmpeg -v error -y -i out/ci/d30/gen/fm_film_raw.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/fm_film.mp4
# app: upload flow, HE recording 28.09 (1_4): 12-17 s choose the video and "who is the surfer" (0-8 s has private photos: never)
ffmpeg -v error -y -ss 12.0 -t 5.0 -i app-screens/ScreenRecording_09-28-2026_10-56-35_1_4.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/fm_app.mp4
mkdir -p out/ci/d30/review; for f in $G/fm_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d30/review/cut_$n.jpg; done
ls -la $G/fm_*
