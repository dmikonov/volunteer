# 28.10 drop reel HE + EN: fetch new HE L1 takes, then generic build
set -x
bash tools/reel/ci/d28_takes.sh
timeout 2700 bash tools/reel/ci/build_reels.sh
