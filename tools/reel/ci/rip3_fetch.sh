# 22.10 rip v3: download stock candidates (Pexels/Pixabay/Mixkit, free commercial licence), keep only contact sheets + small proxies
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/rip3/stock; mkdir -p $O /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
while read n u; do
  [ -z "$n" ] && continue
  curl -sSfL -A "$UA" --retry 2 -o /tmp/st/$n.mp4 "$u" || { echo "FAIL $n" >> $O/fetch.log; continue; }
  I=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/$n.mp4 | tr '\n' ' ')
  echo "OK $n $I $(stat -c%s /tmp/st/$n.mp4)" >> $O/fetch.log
  ffmpeg -nostdin -v error -y -i /tmp/st/$n.mp4 -vf "fps=1,scale=320:-2,drawtext=text='$n %{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.5,tile=6x4" -frames:v 1 $O/${n}_sheet.jpg
  ffmpeg -nostdin -v error -y -ss 2 -i /tmp/st/$n.mp4 -frames:v 1 -vf "scale=1280:-2" -q:v 3 $O/${n}_still.jpg
done < tools/reel/ci/rip3_list.txt
ls -la $O
