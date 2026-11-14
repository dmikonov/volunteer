# 29.10: stock survey for drop-in (Pexels free licence). Probe file URL patterns, download, sheets 2 fps.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d29/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
probe(){ id=$1
  for q in "uhd_2560_1440" "hd_1920_1080" "uhd_1440_2560" "hd_1080_1920" "uhd_3840_2160" "uhd_2160_3840" "hd_1280_720" "hd_720_1280" "sd_960_540" "sd_540_960"; do
    for f in 25 30 24 50 60; do u="https://videos.pexels.com/video-files/$id/$id-${q}_${f}fps.mp4"
      c=$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" -I --connect-timeout 8 -m 15 "$u"); [ "$c" = 200 ] && { echo "$id $u"; return; }
    done; done; echo "$id NONE"; }
for id in $(grep -v '^#' tools/reel/ci/d29_ids.txt); do probe $id & sleep 0.3; done > $R/resolved.txt; wait
cat $R/resolved.txt
while read id u; do [ "$u" = NONE ] && continue
  ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/p$id.mp4 "$u" && ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/p$id.mp4 > $R/p${id}_info.txt
    ffmpeg -nostdin -v error -y -i /tmp/st/p$id.mp4 -vf "fps=2,scale=-2:200,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x6" -frames:v 1 $R/p${id}_sheet.jpg ) &
done < $R/resolved.txt; wait
ls -la $R
