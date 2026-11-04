# fork A 21.10: download Wan clips (full URLs) into out/ci/<reel>/gen/ + 0.2 s sheets
set -x
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
while read r n u; do O=out/ci/$r/gen; mkdir -p $O; curl -sSfLo $O/$n.mp4 "$u" || echo "FAIL $n"
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=180:-1,drawtext=text='%{pts\:hms}':x=3:y=3:fontsize=14:fontcolor=yellow,tile=6x3" -frames:v 1 $O/${n}_sheet.jpg
  ffprobe -v error -show_entries stream=width,height,duration -of csv=p=0 $O/$n.mp4 > $O/${n}_info.txt; done < tools/reel/ci/fetch_a.txt
