# D+3 26.10: Wan clips (new ones) + stock candidates -> sheets (mixkit: 1080 then 720 fallback)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d26/gen; S=out/ci/d26/stock; mkdir -p $O $S /tmp/st
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/d26_gen_list.txt
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
one(){ n=$1; u=$2; S=out/ci/d26/stock
  curl -sSfL -A "$UA" --connect-timeout 15 -m 200 -o /tmp/st/$n.mp4 "$u" || { u2=${u/-1080.mp4/-720.mp4}; curl -sSfL -A "$UA" -m 200 -o /tmp/st/$n.mp4 "$u2" || { echo "FAIL $n"; return; }; }
  I=$(timeout 20 ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/$n.mp4 | tr '\n' ' ')
  echo "OK $n $I"
  timeout 120 ffmpeg -nostdin -v error -y -t 24 -i /tmp/st/$n.mp4 -vf "fps=1,scale=240:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=14:fontcolor=yellow,tile=6x4" -frames:v 1 $S/${n}_sheet.jpg
}
export -f one
cat tools/reel/ci/d26_stock_list.txt | xargs -P 6 -L 1 bash -c 'one "$0" "$1"' > $S/fetch.log 2>&1
cat $S/fetch.log; ls -la $O $S
