# 24.10 foam5 (Dima ok 23.10 14:39): hook question + 3 rules list that stays + SurfTribe app line + save. Clips d24/gen.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
printf 'foam5_he\nfoam5_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48
bash tools/reel/ci/build_reels.sh
git checkout tools/reel/ci/NAMES 2>/dev/null || true  # tracked file must stay unchanged or publish rebase fails
