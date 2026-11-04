# 29.10 night: drop-in reel, Mixkit lineup/aerial candidates (free licence). Download 1080 (or 720), 2 fps sheets.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d29c/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 1074 1070 1071 38927 38933 38939 1163 1075 1127 1128 21286 1076 36833; do
 ( for q in 1080 720 360; do u=https://assets.mixkit.co/videos/$id/$id-$q.mp4; curl -sSfL -A "$UA" -m 200 -o /tmp/st/m$id.mp4 "$u" && { echo "$id $u" >> $R/resolved.txt; break; }; done
   [ -s /tmp/st/m$id.mp4 ] || { echo "$id NONE" >> $R/resolved.txt; exit 0; }
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/m$id.mp4 > $R/m${id}_info.txt
   ffmpeg -nostdin -v error -y -i /tmp/st/m$id.mp4 -vf "fps=2,scale=-2:200,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x6" -frames:v 1 $R/m${id}_sheet.jpg ) &
done; wait
for id in 856422 854351; do u=$(grep "^$id " out/ci/d29/review/resolved.txt | cut -d' ' -f2); curl -sSfL -A "$UA" -m 200 -o /tmp/st/p$id.mp4 "$u" && ffmpeg -nostdin -v error -y -i /tmp/st/p$id.mp4 -vf "fps=4,scale=-2:240,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x6" -frames:v 1 $R/p${id}_sheet4.jpg & done; wait
ls -la $R
