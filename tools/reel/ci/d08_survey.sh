# 08.11 night: HE+EN 11.11 "count sets" (М05). Survey Mixkit shoots with sets / lineup: 389xx (same beach from above), 514xx (same shoot), 1068, 1163, 21286, 1071.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d08/review; mkdir -p $R /tmp/st out/ci/d08/src
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 38939 38933 38927 51459 51458 51460 1068 1163 21286 1071; do
 ( for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/st/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done
   cp /tmp/st/m$id.mp4 out/ci/d08/src/m$id.mp4
   d=$(ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 /tmp/st/m$id.mp4 | tr '\n' ' '); echo "m$id $d" >> $R/dur.txt
   ffmpeg -nostdin -v error -y -i /tmp/st/m$id.mp4 -vf "fps=1,scale=480:-2,drawtext=text='m$id %{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=4x5" -frames:v 1 -q:v 4 $R/sheet_m$id.jpg ) &
done; wait
cat $R/dur.txt; ls -la $R
