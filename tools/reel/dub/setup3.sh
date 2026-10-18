# Sandbox setup for the Hebrew dub/rebuild tools (18.10). usage: bash setup3.sh <git ref> "<EN reel media_url>"
REF=${1:-surftribe-media}; ENURL="$2"
G=https://raw.githubusercontent.com/dmikonov/volunteer/$REF
mkdir -p /s17/po /s17/heb /s17/f5/fl/dev /s17/f5t/u /s17/stock/hd /s17/dub
curl -sSf -o /tmp/setup2.sh $G/tools/reel/setup2.sh && bash /tmp/setup2.sh $REF > /s17/setup2.log 2>&1
pip install -q torch==2.11.0+cpu torchaudio==2.11.0+cpu --index-url https://download.pytorch.org/whl/cpu > /dev/null 2>&1 || echo TORCHFAIL
pip install -q faster-whisper editdistance librosa soundfile gradio_client demucs > /dev/null 2>&1 || echo PIPFAIL
pip uninstall -y -q torchcodec > /dev/null 2>&1
for f in dub.py build_he.py beginners5_he_v2.json; do curl -sSf -o /s17/dub/$f $G/tools/reel/dub/$f; done
cd /s17/stock/hd
for u in https://assets.mixkit.co/videos/1032/1032-1080.mp4 https://cdn.coverr.co/videos/coverr-serene-surfer-gazing-at-the-sea/1080p.mp4 https://assets.mixkit.co/videos/51459/51459-1080.mp4 https://cdn.coverr.co/videos/coverr-surfer-catching-a-wave-5342/1080p.mp4 https://cdn.coverr.co/videos/coverr-a-man-waxing-a-surfboard-359/1080p.mp4 https://cdn.coverr.co/videos/coverr-surfer-walks-towards-waves/1080p.mp4 https://cdn.coverr.co/videos/coverr-a-female-surfer-waiting-for-a-wave-8785/1080p.mp4 https://assets.mixkit.co/videos/38939/38939-1080.mp4 https://assets.mixkit.co/videos/1127/1127-1080.mp4 https://cdn.coverr.co/videos/coverr-guy-surfing-in-the-sea-9468/1080p.mp4; do n=$(echo $u | sed 's#.*videos/##;s#/#_#g'); curl -sL -A Mozilla -o $n $u & done; wait
cd /s17/po && [ -n "$ENURL" ] && curl -sL -o en.mp4 "$ENURL" && ffmpeg -v error -y -i en.mp4 -vn -ac 2 -ar 44100 en.wav && python3 -m demucs --two-stems=vocals -n htdemucs -o /s17/heb/sep /s17/po/en.wav > /s17/demucs.log 2>&1
cd /s17/f5 && python3 -c "from huggingface_hub import hf_hub_download as d; import shutil; shutil.copy(d('google/fleurs','data/he_il/audio/dev.tar.gz',repo_type='dataset'),'dev.tar.gz'); shutil.copy(d('google/fleurs','data/he_il/dev.tsv',repo_type='dataset'),'dev.tsv')" && tar xzf dev.tar.gz -C fl dev/12632262789732552882.wav; rm -f dev.tar.gz
python3 -c "from faster_whisper import WhisperModel; WhisperModel('ivrit-ai/whisper-large-v3-turbo-ct2',device='cpu',compute_type='int8')" > /dev/null 2>&1
ls -la /s17/stock/hd /s17/heb/sep/htdemucs/en /s17/f5/fl/dev
echo SETUP3DONE
