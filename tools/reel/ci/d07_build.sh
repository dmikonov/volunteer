# 07.11 night: HE 10.11 warmup_he r3 + EN 10.11 warmup2_en r1 (Coverr Madeira, one man)
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
printf "warmup_he\nwarmup2_en\n" > tools/reel/ci/NAMES
timeout 2700 bash tools/reel/ci/build_reels.sh
