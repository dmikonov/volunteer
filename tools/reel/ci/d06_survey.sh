# 06.11 night: stock survey for HE "keys and phone" (one surfer: Pexels 5905xxx series, Taryn Elliott 8713xxx) + Mixkit key shots.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d06/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
probe(){ id=$1
  for q in "uhd_2560_1440" "hd_1920_1080" "uhd_1440_2560" "hd_1080_1920" "uhd_3840_2160" "uhd_2160_3840" "hd_1280_720" "hd_720_1280"; do
    for f in 25 30 24 60 50; do u="https://videos.pexels.com/video-files/$id/$id-${q}_${f}fps.mp4"
      c=$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" -I --connect-timeout 8 -m 15 "$u"); [ "$c" = 200 ] && { echo "$id $u"; return; }
    done; done; echo "$id NONE"; }
( for id in $(seq 5905088 5905176) $(seq 8713100 8713124); do probe $id & sleep 0.25; done; wait ) > $R/resolved.txt
for id in 28231 24454 23993; do for q in 1080 720; do curl -sSfL -A "$UA" -m 200 -o /tmp/st/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && echo "$id mixkit-$q" >> $R/resolved.txt && break; done; done
grep -v NONE $R/resolved.txt
while read id u; do [ "$u" = NONE ] && continue; case $u in mixkit*) continue;; esac
  ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/p$id.mp4 "$u" ) &
done < $R/resolved.txt; wait
for f in /tmp/st/*.mp4; do n=$(basename $f .mp4)
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of csv=p=0 $f > $R/${n}_info.txt
  ffmpeg -nostdin -v error -y -i $f -vf "fps=2,scale=-2:160,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x4" -frames:v 1 $R/${n}_sheet.jpg & done; wait
ls -la $R
