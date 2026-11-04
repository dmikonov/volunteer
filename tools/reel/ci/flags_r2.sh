# 21.10 fork C round 2: fetch 2 new clips for flags_he, sheets, then the regular build
set -x
O=out/ci/flags/gen; mkdir -p $O
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
while read n u; do curl -sSfLo $O/$n.mp4 "$u"; ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=200:-1,tile=6x3" -frames:v 1 $O/${n}_sheet.jpg; done < tools/reel/ci/fetch_flags2_list.txt
bash tools/reel/ci/build_reels.sh
