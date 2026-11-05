# 06.11 night: HE 06.11 "where to leave the car key" (Л, быт). Generated: Z-Image Turbo 61101/61107/61104/61108 + Wan 2.2 (hand/key/lockbox/friend/worried surfer). Real: Pexels 8713110 (car at dawn), 8713112 (walking into water), 8713104 (shore), Taryn Elliott. App: HE recording 28.09 15:24 replay.
[ -f /s17/gen/ky_app.mp4 ] && exit 0
G=/s17/gen; R=out/ci/d06k/review; mkdir -p $G /tmp/px $R out/ci/d06k/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
while read n u; do [ -s /tmp/px/$n.mp4 ] || curl -sSfL -m 120 -o /tmp/px/$n.mp4 "$u" || echo "FETCH FAIL $n"; cp /tmp/px/$n.mp4 out/ci/d06k/gen/$n.mp4 2>/dev/null; done < tools/reel/ci/d06k_list.txt
for id in 8713110 8713112 8713104; do [ -s /tmp/px/p$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p$id.mp4 https://videos.pexels.com/video-files/$id/$id-hd_1080_1920_25fps.mp4; done
# gen clip -> 1080x1920 (Wan gives ~480x832)
g(){ n=$1; ss=$2; t=$3; o=$4; ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$n.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$o.mp4; }
p(){ id=$1; ss=$2; t=$3; o=$4; ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/p$id.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$o.mp4; }
g w_tyre 0 3.5 ky_tyre
g w_worry 0 3.5 ky_worry
g w_lock 0 3.0 ky_lock
g w_friend 0 3.5 ky_friend
g w_calm 0 3.5 ky_calm
p 8713110 0.0 4.0 ky_car
p 8713112 2.0 5.0 ky_walk
p 8713104 4.0 4.0 ky_tmrw
ffmpeg -v error -y -ss 17.6 -t 4.0 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/ky_app.mp4
for f in $G/ky_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=5,scale=180:-2,tile=18x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/ky_*
