# 09.11 night: 12.11 last wave HE+EN.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d09/takes
python3 - <<'PY'
import json, os, subprocess as sp, hashlib
p='tools/reel/specs/lastwave_he.takes.json'; tk=json.load(open(p)); out=[]
for i,u in tk:
    f='out/ci/d09/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    if not os.path.exists(f): sp.run(['curl','-sSfL','--retry','2','-m','60','-o',f,u])
    if os.path.exists(f) and os.path.getsize(f)>2000: out.append([i,'file://'+os.path.abspath(f)])
    else: print('TAKE LOST',i,u[-30:])
json.dump(out,open(p,'w'))
PY
printf "lastwave_he\nlastwave_en\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
