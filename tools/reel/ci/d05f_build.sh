# 05.11 night: HE 05.11 forecast reading (period, wind, height). NAMES set here at runtime only (warmup_en runs in parallel and uses the tracked NAMES).
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
echo forecast_he > tools/reel/ci/NAMES
mkdir -p out/ci/d05f; bash -x tools/reel/specs/forecast_he.prep.sh > out/ci/d05f/prep.log 2>&1
timeout 2700 bash tools/reel/ci/build_reels.sh
