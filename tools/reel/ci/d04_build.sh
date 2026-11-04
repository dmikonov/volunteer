# 04.11 night: first winter storm (HE, 07.11)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
bash tools/reel/ci/d04_takes.sh
mkdir -p out/ci/d04; bash -x tools/reel/specs/storm_he.prep.sh > out/ci/d04/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
