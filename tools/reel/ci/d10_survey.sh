# 10.11 night: 13.11 HE lightning (Б21) + EN whitewater to green waves (Т202). Survey real shots.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d10/review; S=out/ci/d10/src; mkdir -p $R $S /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
probe(){ id=$1
  for q in "hd_1080_1920" "uhd_1440_2560" "uhd_2160_3840" "hd_1920_1080" "uhd_2560_1440" "uhd_3840_2160" "hd_720_1280" "hd_1280_720"; do
    for f in 25 30 24 50 60; do u="https://videos.pexels.com/video-files/$id/$id-${q}_${f}fps.mp4"
      c=$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" -I --connect-timeout 8 -m 15 "$u"); [ "$c" = 200 ] && { echo "$id $u"; return; }
    done; done; echo "$id NONE"; }
for id in 4059 48918 47698 47949 29354 48854 17969 32463 9624 21286 1163 36924 1075 1128 1068 6892; do ( for q in 1080 720; do curl -sSfL -A "$UA" -m 280 -o $S/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done ) & done
( P=$(curl -sSL -A "$UA" -m 60 https://coverr.co/fr/videos/faire-du-surf-sur-un-surfboard | grep -o 'https://cdn.coverr.co/videos/[^"/]*/1080p.mp4' | head -1); echo "coverr $P" > $R/coverr.txt; [ -n "$P" ] && curl -sSfL -A "$UA" -m 280 -o $S/csurf.mp4 "$P" ) &
for id in $(seq 8713100 8713120) $(seq 7938100 7938112) $(seq 7938428 7938450); do probe $id & sleep 0.2; done > $R/resolved.txt; wait
grep -v NONE $R/resolved.txt
while read id u; do [ "$u" = NONE ] && continue; [ -f out/ci/d09/src/p$id.mp4 ] && { cp out/ci/d09/src/p$id.mp4 $S/; continue; }
  curl -sSfL -A "$UA" -m 280 -o $S/p$id.mp4 "$u" & done < $R/resolved.txt; wait
for f in $S/*.mp4; do n=$(basename $f .mp4); ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/$n.info
 ffmpeg -nostdin -v error -y -i $f -vf "fps=2,scale=-2:150,drawtext=text='$n %{pts\:hms}':x=3:y=3:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=12x3" -frames:v 1 $R/${n}_sheet.jpg & done; wait
# keep repo small: only clips we may use stay in src (decided after review); big files > 60MB dropped now
find $S -size +60M -delete; ls -la $S $R; cat $R/*.info
