# 12.11 night: cache F5 takes for rchan_he (hf.space links die within the hour)
mkdir -p out/ci/d12/takes
python3 - <<'PY'
import json, os, subprocess as sp, hashlib
tk=json.load(open('tools/reel/specs/rchan_he.takes.json'))
for i,u in tk:
    f='out/ci/d12/takes/'+hashlib.md5(u.encode()).hexdigest()[:12]+'.wav'
    sp.run(['curl','-sSfL','--retry','2','-m','60','-o',f,u]); print(i, f, os.path.getsize(f) if os.path.exists(f) else 'LOST')
PY
