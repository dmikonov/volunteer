# 05.11 night: EN 08.11 warm-up (Pexels 62996xx, one family on one beach, free licence): full-res stills to pick crops
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d05w/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 6299678 6299679 6299681 6299684 6299685 6299691 6299692 6299694; do
 ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/p$id.mp4 "https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_25fps.mp4" || echo "FAIL $id"
   for t in 0 2 4 6 8 10 12; do ffmpeg -nostdin -v error -y -ss $t -i /tmp/st/p$id.mp4 -frames:v 1 -vf "scale=1280:-2,drawtext=text='$id t$t':x=10:y=10:fontsize=28:fontcolor=yellow:box=1:boxcolor=black@0.6" -q:v 4 $R/p${id}_t$t.jpg; done ) &
done; wait
ls -la $R
