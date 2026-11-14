# 12.11 night: 15.11 HE+EN rip channel (Т301). Takes cached in out/ci/d12/takes, build both in one run.
set -x
python3 - <<'PY'
import json, os, hashlib
p='tools/reel/specs/rchan_he.takes.json'; tk=json.load(open(p)); out=[]
for i,u in tk:
    f='out/ci/d12/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    if not os.path.exists(f): __import__('subprocess').run(['curl','-sSfL','--retry','2','-m','60','-o',f,u])
    if os.path.exists(f) and os.path.getsize(f)>2000: out.append([i,'file://'+os.path.abspath(f)])
    else: print('TAKE LOST',i)
json.dump(out,open(p,'w'))
PY
printf "rchan_he\nrchan_en\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
for k in rchan_he rchan_en; do cp /s17/rp/$k/voice.log out/ci/$k/voice_full.log 2>/dev/null; done
true
