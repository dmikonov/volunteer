# D+3 27.10: survey candidate stock (Pexels free licence): download, keep 1080p-height copies, contact sheets 1 fps
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
S=out/ci/d27/src; R=out/ci/d27/review; mkdir -p $S $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
while read n u; do [ -z "$n" ] && continue; ( curl -sSfL -A "$UA" --connect-timeout 15 -m 300 -o /tmp/st/$n.mp4 "$u" || echo "FAIL $n" ) & done < tools/reel/ci/d27_stock_list.txt
wait
for f in /tmp/st/*.mp4; do n=$(basename $f .mp4)
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 $f > $R/${n}_info.txt
  ffmpeg -nostdin -v error -y -i $f -vf "scale=-2:1080:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 19 -preset fast $S/$n.mp4
  ffmpeg -nostdin -v error -y -i $S/$n.mp4 -vf "fps=1,scale=-2:240,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x7" -frames:v 1 $R/${n}_sheet.jpg
done
ls -la $S $R
