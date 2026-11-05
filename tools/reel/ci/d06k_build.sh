# 06.11 night: HE 06.11 keys. NAMES set at runtime only.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
echo keys_he > tools/reel/ci/NAMES
mkdir -p out/ci/d06k; bash -x tools/reel/specs/keys_he.prep.sh > out/ci/d06k/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
