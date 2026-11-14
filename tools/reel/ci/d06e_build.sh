# 06.11 night: HE 09.11 ears. NAMES set at runtime only.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
echo ears_he > tools/reel/ci/NAMES
mkdir -p out/ci/d06e; bash -x tools/reel/specs/ears_he.prep.sh > out/ci/d06e/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
