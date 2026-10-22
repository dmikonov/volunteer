# rip v3: build only
set -x
printf "rip3_en\nrip3_he\n" > tools/reel/ci/NAMES
timeout 2400 bash tools/reel/ci/build_reels.sh
