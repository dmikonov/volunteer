# 11.11 night: 14.11 HE winter beginner spot (Сп01, why-form) + EN why ride sideways (Т205 trim). Survey real shots.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d11/review; S=out/ci/d11/src; mkdir -p $R $S
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
probe(){ id=$1
  for q in "hd_1080_1920" "uhd_1440_2560" "uhd_2160_3840" "hd_1920_1080" "uhd_2560_1440" "uhd_3840_2160" "hd_720_1280" "hd_1280_720" "sd_960_540" "sd_640_360"; do
    for f in 25 30 24 50 60 29 23; do u="https://videos.pexels.com/video-files/$id/$id-${q}_${f}fps.mp4"
      c=$(curl -s -o /dev/null -w '%{http_code}' -A "$UA" -I --connect-timeout 8 -m 15 "$u"); [ "$c" = 200 ] && { echo "$id $u"; return; }
    done; done; echo "$id NONE"; }
for id in 9823083 11471497 5902539 5902497 31341238 20256023 18224893 36755893 4093785 17092117 13169680 32889385 31392109 4961454 15456695 30137271 6989125 5305442; do probe $id & sleep 0.3; done > $R/resolved.txt; wait
grep -v NONE $R/resolved.txt
while read id u; do [ "$u" = NONE ] && continue; curl -sSfL -A "$UA" -m 280 -o $S/p$id.mp4 "$u" & done < $R/resolved.txt; wait
for f in $S/*.mp4; do n=$(basename $f .mp4); ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/$n.info
 ffmpeg -nostdin -v error -y -i $f -vf "fps=2,scale=-2:150,drawtext=text='$n %{pts\:hms}':x=3:y=3:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=12x3" -frames:v 1 $R/${n}_sheet.jpg & done; wait
find $S -size +60M -delete; ls -la $S $R; cat $R/*.info
