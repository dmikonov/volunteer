# 04.11 night: Mixkit survey for 07.11 HE (first winter storm: myth "storm = good waves") and EN (shallow reef: fall flat). Free licence.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d04/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
: > $R/list.txt
for q in storm stormy-sea rough-sea sea-storm big-waves waves lightning thunderstorm windy-beach wind surfer surfing surf beach-storm reef shallow-water wipeout clouds-over-sea; do
 for p in 1 2 3; do curl -sSL -A "$UA" -m 40 "https://mixkit.co/free-stock-video/$q/?page=$p" | grep -o 'free-stock-video/[a-z0-9-]*-[0-9]\{2,6\}/' | sort -u | sed "s|^|$q |" >> $R/list.txt; done
done
sort -u -k2 $R/list.txt -o $R/list.txt; wc -l $R/list.txt
grep -Ei 'storm|rough|wave|lightning|thunder|wind|surf|reef|shallow|cloud|sea|ocean|beach|fall' $R/list.txt | awk '{print $2}' | sed -E 's|.*-([0-9]+)/$|\1 &|' | sort -u -k1,1 > $R/cand.txt
wc -l $R/cand.txt
n=0
while read id slug; do n=$((n+1)); [ $n -gt 160 ] && break
 ( for qq in 360 720; do curl -sSfL -A "$UA" -m 100 -o /tmp/st/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$qq.mp4 && break; done
   [ -s /tmp/st/m$id.mp4 ] || exit 0
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of csv=p=0 /tmp/st/m$id.mp4 | tr '\n' ' ' > $R/m${id}_info.txt; echo " $slug" >> $R/m${id}_info.txt
   ffmpeg -nostdin -v error -y -i /tmp/st/m$id.mp4 -vf "fps=1,scale=-2:160,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x3" -frames:v 1 $R/m${id}_sheet.jpg ) &
 [ $((n % 16)) -eq 0 ] && wait
done < $R/cand.txt; wait
ls $R | wc -l
