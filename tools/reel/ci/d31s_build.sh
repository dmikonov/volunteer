# 31.10 night: EN Stop splashing (31.10)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d31s; bash -x tools/reel/specs/splash_en.prep.sh > out/ci/d31s/prep.log 2>&1; ls -la /s17/gen >> out/ci/d31s/prep.log
timeout 2700 bash tools/reel/ci/build_reels.sh
