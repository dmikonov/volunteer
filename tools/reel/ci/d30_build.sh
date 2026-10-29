# 30.10 film a friend HE
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
mkdir -p out/ci/d30; bash -x tools/reel/specs/film_he.prep.sh > out/ci/d30/prep_film.log 2>&1; ls -la /s17/gen >> out/ci/d30/prep_film.log
timeout 2700 bash tools/reel/ci/build_reels.sh
