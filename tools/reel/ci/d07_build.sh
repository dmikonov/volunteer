# 07.11 night: HE 10.11 warmup_he (Coverr Madeira, one man), F5 voice 3 takes in specs/warmup_he.takes.json
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
echo warmup_he > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
