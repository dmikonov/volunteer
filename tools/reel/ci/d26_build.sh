# D+3 26.10 build: rain_he + tide_en with the generic pipeline (NAMES set only inside this CI run, the shared NAMES file is not committed)
printf 'rain_he\ntide_en\n' > tools/reel/ci/NAMES
export REEL_MUSIC=mixkit-48  # 23.10 rip = mixkit-83, neighbours alternate (24, 26 = 48; 25 = 83)
bash tools/reel/ci/build_reels.sh
git checkout tools/reel/ci/NAMES 2>/dev/null || true
