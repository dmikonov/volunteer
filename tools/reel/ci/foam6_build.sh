# foam6 (23.10): foam5 script/voice on real clips (Sept shoot) + Mixkit + one clean LTX shot
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
printf 'foam6_he\nfoam6_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48
bash tools/reel/ci/build_reels.sh
