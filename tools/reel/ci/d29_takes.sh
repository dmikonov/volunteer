# 29.10: F5 voice-3 takes (HE drop-in reel, with nikud) into out/ci/d29/takes
set -x
O=out/ci/d29/takes; mkdir -p $O
while read i s u; do [ -z "$i" ] && continue; f=$O/L$((i+1))_s$s.wav; [ -s $f ] && continue; curl -sSfL --retry 2 --connect-timeout 15 -m 120 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d29_takes_list.txt
ls -la $O
while read i s u; do [ -z "$i" ] && continue; f=$O/L$((i+1))_b$s.wav; [ -s $f ] && continue; curl -sSfL --retry 2 --connect-timeout 15 -m 120 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d29b_takes_list.txt
ls -la $O
