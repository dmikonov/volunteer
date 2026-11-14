# foam5 EN r2: shorter titles (hook, app, save) so they don't hit the foam / app card / list
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
printf 'foam5_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48
bash tools/reel/ci/build_reels.sh
