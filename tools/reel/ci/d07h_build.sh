# 07.11 night: HE 10.11 warmup_he + EN 10.11 warmup2_en (Coverr Madeira, one man). F5 takes are cached in out/ci/d07/takes (hf.space links die).
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d07/takes
python3 - <<'PY'
import json, os, subprocess as sp, hashlib
p='tools/reel/specs/warmup_he.takes.json'; tk=json.load(open(p)); out=[]
for i,u in tk:
    f='out/ci/d07/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    if not os.path.exists(f): sp.run(['curl','-sSfL','--retry','2','-m','60','-o',f,u])
    if os.path.exists(f) and os.path.getsize(f)>2000: out.append([i,'file://'+os.path.abspath(f)])
    else: print('TAKE LOST',i,u[-30:])
json.dump(out,open(p,'w'))
PY
printf "warmup_he\nwarmup2_en\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
