# 04.11: F5 voice-3 takes (HE storm 07.11) into out/ci/d04/takes
O=out/ci/d04/takes3; mkdir -p $O
while read i s u; do [ -z "$i" ] && continue; f=$O/L$((i+1))_s$s.wav; [ -s $f ] && continue; curl -sSfL --retry 2 --connect-timeout 15 -m 120 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d04_takes_list.txt
ls -la $O
