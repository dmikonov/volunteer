# 02.11 chest up EN
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d30; bash -x tools/reel/specs/chest_en.prep.sh > out/ci/d30/prep_chest.log 2>&1; ls -la /s17/gen >> out/ci/d30/prep_chest.log
timeout 2700 bash tools/reel/ci/build_reels.sh
