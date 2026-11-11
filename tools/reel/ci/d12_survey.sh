# 12.11 night: 15.11 HE+EN "rip as a paddle-out channel" (Т301). Survey real shots (Bondi aerials, channel next to a break).
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d12/review; S=out/ci/d12/src; mkdir -p $R $S
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
probe(){ id=$1
  for q in "hd_1920_1080" "hd_1080_1920" "uhd_2560_1440" "uhd_1440_2560" "hd_1280_720" "hd_720_1280" "uhd_3840_2160" "uhd_2160_3840"; do
    for f in 25 30 24 50 60 29 23; do u="https://videos.pexels.com/video-files/$id/$id-${q}_${f}fps.mp4"
      c=$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" -I --connect-timeout 8 -m 15 "$u"); [ "$c" = 200 ] && { echo "$id $u"; return; }
    done; done; echo "$id NONE"; }
for id in 31845107 31845098 32889390 32889391 8334404 15317073 7498300 10540776 6825302 6989125 38005980 33731641; do probe $id & sleep 0.3; done > $R/resolved.txt; wait
cat $R/resolved.txt
while read id u; do [ "$u" = NONE ] && continue; curl -sSfL -A "$UA" -m 280 -o $S/p$id.mp4 "$u" & done < $R/resolved.txt
for id in 1075 36924 1163 21286; do ( for q in 1080 720; do curl -sSfL -A "$UA" -m 280 -o $S/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done ) & done; wait
for f in $S/*.mp4; do n=$(basename $f .mp4); ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/$n.info
 d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f); fp=$(python3 -c "print(max(1,min(4,36/float('$d'))))")
 ffmpeg -nostdin -v error -y -i $f -vf "fps=$fp,scale=-2:200,drawtext=text='$n %{pts\:hms}':x=3:y=3:fontsize=15:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=9x4" -frames:v 1 $R/${n}_sheet.jpg & done; wait
find $S -size +60M -delete; ls -la $S $R; cat $R/*.info
