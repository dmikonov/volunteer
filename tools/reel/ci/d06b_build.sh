# 06.11 night: HE keys (06.11) + HE ears (09.11) together. NAMES set at runtime only.
set -x
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
printf "keys_he\nears_he\n" > tools/reel/ci/NAMES
timeout 2900 bash tools/reel/ci/build_reels.sh
