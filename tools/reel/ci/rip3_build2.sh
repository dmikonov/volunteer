# rip v3 r4: fetch takes + Wan clips (timeouts), then build rip3 EN+HE
set -x
bash tools/reel/ci/rip3_takes.sh
bash tools/reel/ci/rip3_gen.sh
printf "rip3_en\nrip3_he\n" > tools/reel/ci/NAMES
bash tools/reel/ci/build_reels.sh
