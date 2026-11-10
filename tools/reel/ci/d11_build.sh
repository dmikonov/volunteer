# 11.11 night: 14.11 HE spot (Сп01 why-form). Cache F5 takes, build.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d11/takes out/ci/d11/review
python3 - <<'PY'
import json, os, subprocess as sp, hashlib
p='tools/reel/specs/spot_he.takes.json'; tk=json.load(open(p)); out=[]
for i,u in tk:
    if u.startswith('file://'): out.append([i,u]); continue
    f='out/ci/d11/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    if not os.path.exists(f): sp.run(['curl','-sSfL','--retry','2','-m','60','-o',f,u])
    if os.path.exists(f) and os.path.getsize(f)>2000: out.append([i,'file://'+os.path.abspath(f)])
    else: print('TAKE LOST',i,u[-30:])
json.dump(out,open(p,'w'))
PY
printf "spot_he\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
cp /s17/rp/spot_he/voice.log out/ci/spot_he/voice_full.log 2>/dev/null
