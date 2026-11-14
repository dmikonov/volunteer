# 24.10 foam4 HE+EN: fetch Wan clips + HE takes, then build (NAMES set only inside this run)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d24/gen; T=out/ci/d24/takes; mkdir -p $O $T
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/d24_gen_list.txt
while read i s u; do [ -z "$i" ] && continue; f=$T/L$((i+1))_s$s.wav; [ -f $f ] && continue; curl -sSfL --retry 3 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d24_takes_list.txt
printf 'foam4_he\nfoam4_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48  # 23.10 rip = mixkit-83, neighbours alternate (24, 26 = 48; 25 = 83)
bash tools/reel/ci/build_reels.sh
git checkout tools/reel/ci/NAMES 2>/dev/null || true
