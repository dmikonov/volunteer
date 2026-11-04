# 05.11 night: EN 08.11 warm-up (Ф01, moved from 10.11)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d05w; bash -x tools/reel/specs/warmup_en.prep.sh > out/ci/d05w/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
