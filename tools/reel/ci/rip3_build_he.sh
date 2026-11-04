# rip v3: HE only rebuild
set -x
bash tools/reel/ci/rip3_takes.sh
printf "rip3_he\n" > tools/reel/ci/NAMES
bash tools/reel/ci/build_reels.sh
