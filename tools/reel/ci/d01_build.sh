# 01.11 night: tar on feet (HE, 04.11)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
bash tools/reel/ci/d01_takes.sh
mkdir -p out/ci/d01; bash -x tools/reel/specs/tar_he.prep.sh > out/ci/d01/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
