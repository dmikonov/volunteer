# 24.10 foam4 HE+EN: fetch Wan clips + HE takes, then build (NAMES set only inside this run)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d25/gen; T=out/ci/d25/takes; mkdir -p $O $T
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/d25_gen_list.txt
while read i s u; do [ -z "$i" ] && continue; f=$T/L$((i+1))_s$s.wav; [ -f $f ] && continue; curl -sSfL --retry 3 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d25_takes_list.txt
printf 'flags5_he\nsets5_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-83  # 25.10: neighbours 24 and 26 are mixkit-48
bash tools/reel/ci/build_reels.sh
git checkout tools/reel/ci/NAMES 2>/dev/null || true
