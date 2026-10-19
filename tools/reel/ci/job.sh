set -x
O=out/ci/foam; mkdir -p $O/gen
B=https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/mlgh8/gradio_api/file=/tmp/gradio
get(){ curl -sSfLo $O/gen/$1.mp4 "$B/$2" || curl -sSfLo $O/gen/$1.mp4 "$3"; }
S3=https://backend.composio.dev/api/v3/sl/8CQU-AKqu6
curl -sSfL -o /tmp/g.tar $S3 && tar xf /tmp/g.tar -C $O/gen
ls -la $O/gen
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
for f in $O/gen/f_*.mp4; do ffmpeg -v error -y -i $f -vf "fps=5,scale=200:-1,tile=6x3" -frames:v 1 ${f%.mp4}_sheet.jpg; done
