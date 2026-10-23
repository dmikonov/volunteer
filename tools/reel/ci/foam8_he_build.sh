# foam7 (23.10): foam5 script/voice on real clips (Sept shoot) + Mixkit + one clean LTX shot
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
printf 'foam8_he\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48
bash tools/reel/ci/build_reels.sh
