#!/bin/bash
mkdir -p out/ci/music; python3 tools/reel/ci/musicscan.py > out/ci/music/log.txt 2>&1; cat out/ci/music/log.txt
