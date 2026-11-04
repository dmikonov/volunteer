# 05.11: edge-tts diagnostic (warmup_en voice failed: NoAudioReceived on python 3.14 runner)
set -x
R=out/ci/d05w/tts; mkdir -p $R
python3 --version > $R/log.txt 2>&1
cat > /tmp/t.py <<'PY'
import asyncio, edge_tts, sys
async def m():
    c = edge_tts.Communicate('Three fixes. Five minutes.', sys.argv[1], rate='-10%')
    await c.save(sys.argv[2])
asyncio.run(m()); print('OK', edge_tts.__version__ if hasattr(edge_tts,'__version__') else '')
PY
pip install -q uv >/dev/null 2>&1
for v in 7.2.7 7.2.3 7.0.2 6.1.19; do
  echo "== py3.12 edge-tts $v" >> $R/log.txt
  timeout 120 uv run -q --python 3.12 --with edge-tts==$v python /tmp/t.py en-US-AndrewMultilingualNeural $R/t_$v.mp3 >> $R/log.txt 2>&1 || echo "FAIL $v" >> $R/log.txt
done
pip install -q edge-tts >/dev/null 2>&1; echo "== system $(pip show edge-tts | grep Version)" >> $R/log.txt
timeout 60 python3 /tmp/t.py en-US-AndrewMultilingualNeural $R/t_sys.mp3 >> $R/log.txt 2>&1 || echo FAIL sys >> $R/log.txt
timeout 60 python3 /tmp/t.py en-US-AndrewNeural $R/t_sys2.mp3 >> $R/log.txt 2>&1 || echo FAIL sys AndrewNeural >> $R/log.txt
tail -c 4000 $R/log.txt
