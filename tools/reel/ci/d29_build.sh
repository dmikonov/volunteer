# 29.10 drop-in reel HE + EN
set -x
bash tools/reel/ci/d29_takes.sh
timeout 2700 bash tools/reel/ci/build_reels.sh
