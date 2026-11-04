# D+3 26.10 round 2: fetch new Wan clips + new HE takes, then build rain_he + tide_en
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d26/gen; T=out/ci/d26/takes; mkdir -p $O $T
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/d26_gen_list.txt
while read i s u; do [ -z "$i" ] && continue; f=$T/L$((i+1))_s$s.wav; [ -f $f ] && continue; curl -sSfL --retry 3 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d26_takes_list.txt
bash tools/reel/ci/d26_build.sh
