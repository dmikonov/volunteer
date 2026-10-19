set -x
O=out/ci/foam/gen; mkdir -p $O
B=https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/mlgh8/gradio_api/file=/tmp/gradio
while read n u; do curl -sSfLo $O/$n.mp4 "$B/$u"; done < tools/reel/ci/fetch_list.txt
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
while read n u; do ffmpeg -v error -y -i $O/$n.mp4 -vf "fps=5,scale=200:-1,tile=6x3" -frames:v 1 $O/${n}_sheet.jpg; done < tools/reel/ci/fetch_list.txt
