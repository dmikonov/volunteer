# 04.11 night: new spot and locals (EN, 07.11)
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d04b; bash -x tools/reel/specs/locals_en.prep.sh > out/ci/d04b/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
