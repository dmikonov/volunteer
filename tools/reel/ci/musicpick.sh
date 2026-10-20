#!/bin/bash
mkdir -p out/ci/music
{ sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg > /dev/null; python3 tools/reel/ci/musicpick.py; } > out/ci/music/cand_log.txt 2>&1; cat out/ci/music/cand_log.txt
