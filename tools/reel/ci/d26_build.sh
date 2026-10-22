# D+3 26.10 build: rain_he + tide_en with the generic pipeline (NAMES set only inside this CI run, the shared NAMES file is not committed)
printf 'rain_he\ntide_en\n' > tools/reel/ci/NAMES
bash tools/reel/ci/build_reels.sh
git checkout tools/reel/ci/NAMES 2>/dev/null || true
