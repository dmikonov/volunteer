# New sandbox setup for tools/reel (18.10). usage: bash setup2.sh <git sha or branch>
REF=${1:-surftribe-media}
G=https://raw.githubusercontent.com/dmikonov/volunteer/$REF
mkdir -p /s17/raw /s17/gen /s17/gen2 /s17/tip1 /s17/app /s17/rp
(DEBIAN_FRONTEND=noninteractive apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg curl > /dev/null) || echo APTFAIL
pip install -q opencv-python-headless numpy playwright edge-tts huggingface_hub > /dev/null 2>&1 || echo PIPFAIL
python3 -m playwright install --with-deps chromium > /dev/null 2>&1 || echo PWFAIL
curl -sSf -o /s17/Rubik.ttf $G/appkit/Rubik.ttf
cd /s17/app
for f in ScreenRecording_09-28-2026_10-56-35_1_2 ScreenRecording_09-28-2026_15-24-29_1 ScreenRecording_10-12-2026_13-42-15_1 ScreenRecording_09-26-2026_17-24-44_1; do curl -sSf -o $f.mp4 $G/app-screens/$f.mp4; done
for f in forecast_he_period forecast_en_period forecast_he_water forecast_en_water forecast_he_best forecast_en_best forecast_he_height forecast_en_height; do curl -sSf -o $f.mp4 $G/app-screens/forecast/$f.mp4; done
python3 -c "from huggingface_hub import hf_hub_download as d; print(d('dmikonov/surftribe-drafts','scripts/tip1/audio_fx.py',repo_type='dataset',local_dir='/s17'))"
python3 /s17/scripts/tip1/audio_fx.py 32
cd /s17/rp
for f in voice.py build.py ov.py post.py run.sh loudfix.py; do curl -sSf -o $f $G/tools/reel/$f; done
for k in look_he look_en knees_he knees_en paddle_he paddle_en; do mkdir -p $k; curl -sSf -o $k/spec.json $G/tools/reel/specs/$k.json; done
ls -la /s17 /s17/app /s17/tip1; which ffmpeg
echo SETUPDONE
