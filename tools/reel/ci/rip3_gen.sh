# rip v3: download Wan 2.2 clips listed in rip3_gen_list.txt into out/ci/rip3/gen (keeps existing)
set -x
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || (sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null)
O=out/ci/rip3/gen; mkdir -p $O
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=7x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/rip3_gen_list.txt
ls -la $O
