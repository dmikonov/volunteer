# 06.11 night: ears_he r7 only (app tile lower).
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
echo ears_he > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
