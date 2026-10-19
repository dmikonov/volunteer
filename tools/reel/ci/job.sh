set -x
O=out/ci/foam/gen; mkdir -p $O
B=https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/mlgh8/gradio_api/file=/tmp/gradio
curl -sSfLo $O/f_angle2.mp4 "$B/f8ddceff39a0507b8affa35809b2d2c5123182ca958fad5d92f0cab8e24fcabc/tmplh9hhju9.mp4"
curl -sSfLo $O/f_angle3.mp4 "$B/6153c4fc54f095880ae12cd33b13243ca2102b2dbbc98fe175e3307487ba31e6/tmpta1w7gms.mp4"
curl -sSfLo $O/f_walk.mp4 "$B/123ad27d22dcf6195b9511a9344fd725e80ccb3a2049b2144e1194323bf63462/tmpjtnoky66.mp4"
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
for f in $O/f_angle2.mp4 $O/f_angle3.mp4 $O/f_walk.mp4; do ffmpeg -v error -y -i $f -vf "fps=5,scale=200:-1,tile=6x3" -frames:v 1 ${f%.mp4}_sheet.jpg; done
