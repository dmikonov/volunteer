# 31.10 night: SurfTribe Club for coaches (03.11), HE + EN
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
bash tools/reel/ci/d31_takes.sh
mkdir -p out/ci/d31; bash -x tools/reel/specs/club_en.prep.sh > out/ci/d31/prep.log 2>&1; ls -la /s17/gen >> out/ci/d31/prep.log
timeout 2700 bash tools/reel/ci/build_reels.sh
