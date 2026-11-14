# 22.10 rip v3: download stock candidates (Pexels/Pixabay/Mixkit, free commercial licence), keep only contact sheets + stills (parallel, with timeouts)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/rip3/stock; mkdir -p $O /tmp/st
one(){ n=$1; u=$2; O=out/ci/rip3/stock
  [ -f $O/${n}_sheet.jpg ] && return
  curl -sSfL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36" --connect-timeout 15 -m 180 -o /tmp/st/$n.mp4 "$u" || { echo "FAIL $n"; return; }
  I=$(timeout 20 ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/$n.mp4 | tr '\n' ' ')
  echo "OK $n $I $(stat -c%s /tmp/st/$n.mp4)"
  timeout 120 ffmpeg -nostdin -v error -y -t 30 -i /tmp/st/$n.mp4 -vf "fps=1,scale=320:-2,tile=6x5" -frames:v 1 $O/${n}_sheet.jpg
  timeout 30 ffmpeg -nostdin -v error -y -ss 2 -i /tmp/st/$n.mp4 -frames:v 1 -vf "scale=1280:-2" -q:v 3 $O/${n}_still.jpg
}
export -f one
cat tools/reel/ci/rip3_list.txt | xargs -P 6 -L 1 bash -c 'one "$0" "$1"' > $O/fetch.log 2>&1
ls -la $O
