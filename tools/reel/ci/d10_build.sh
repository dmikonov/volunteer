# 10.11 night: 13.11 HE thunder. Fetch Wan clips (kept in out/ci/d10/gen), cache F5 takes, build.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
W=out/ci/d10/gen; mkdir -p $W out/ci/d10/takes out/ci/d10/review
B=https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/lptw2/gradio_api/file=/tmp/gradio
while read n u; do case $u in http*) U=$u;; *) U=$B/$u;; esac; [ -s $W/$n.mp4 ] || curl -sSfL --retry 2 -m 120 -o $W/$n.mp4 "$U" || echo "WAN LOST $n"; done < tools/reel/ci/d10_wan.txt
python3 - <<'PY'
import json, os, subprocess as sp, hashlib
p='tools/reel/specs/thunder_he.takes.json'; tk=json.load(open(p)); out=[]
for i,u in tk:
    if u.startswith('file://'): out.append([i,u]); continue
    f='out/ci/d10/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    if not os.path.exists(f): sp.run(['curl','-sSfL','--retry','2','-m','60','-o',f,u])
    if os.path.exists(f) and os.path.getsize(f)>2000: out.append([i,'file://'+os.path.abspath(f)])
    else: print('TAKE LOST',i,u[-30:])
json.dump(out,open(p,'w'))
PY
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
for f in $W/*.mp4; do n=$(basename $f .mp4); ffmpeg -nostdin -v error -y -i $f -vf "fps=5,scale=200:-1,tile=9x2" -frames:v 1 out/ci/d10/review/wan_$n.jpg; ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > out/ci/d10/review/wan_$n.info; done
printf "thunder_he\nsunset_en\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
