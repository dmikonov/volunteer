# rip v3: fetch new takes, then generic build of NAMES
set -x
bash tools/reel/ci/rip3_takes.sh
sed -i 's#^bash tools/reel/ci/rip3_gen.sh##' /dev/null
bash tools/reel/ci/build_reels.sh
