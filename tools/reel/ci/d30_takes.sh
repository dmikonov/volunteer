# 30.10: F5 voice-3 takes (HE film-a-friend reel, nikud) into out/ci/d30/takes
O=out/ci/d30/takes; mkdir -p $O
for L in tools/reel/ci/d30_takes_list.txt tools/reel/ci/d30b_takes_list.txt; do [ -f $L ] || continue; p=$(basename $L .txt | sed 's/d30//;s/_takes_list//'); 
while read i s u; do [ -z "$i" ] && continue; f=$O/L$((i+1))_${p}s$s.wav; [ -s $f ] && continue; curl -sSfL --retry 2 --connect-timeout 15 -m 120 -o $f "$u" || echo "FAIL $f"; done < $L; done
ls -la $O
