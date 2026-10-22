# rip v3: save F5 voice-3 takes into out/ci/rip3/takes (L<i>_s<seed>.wav) + Wan clips
set -x
O=out/ci/rip3/takes; mkdir -p $O
while read i s u; do [ -z "$i" ] && continue; f=$O/L$((i+1))_s$s.wav; [ -f $f ] && continue; curl -sSfL --retry 3 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/rip3_takes_list.txt
ls -la $O
bash tools/reel/ci/rip3_gen.sh
