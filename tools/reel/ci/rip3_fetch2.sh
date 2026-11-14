# fetch takes + gen clips
set -x
bash tools/reel/ci/rip3_takes.sh
sudo apt-get update -qq
bash tools/reel/ci/rip3_gen.sh
