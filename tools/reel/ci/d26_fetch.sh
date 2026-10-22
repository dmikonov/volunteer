# 23.10 night: D+3 (26.10) rain HE / tide EN: Wan clips + stock discovery (mixkit/pexels/pixabay pages -> candidate lists)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d26/gen; S=out/ci/d26/stock; mkdir -p $O $S /tmp/st
while read n u; do [ -z "$n" ] && continue; [ -f $O/$n.mp4 ] && continue
  curl -sSfL --retry 3 -o $O/$n.mp4 "$u" || { echo "FAIL $n"; rm -f $O/$n.mp4; continue; }
  ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=216:-2,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg
done < tools/reel/ci/d26_gen_list.txt
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
: > $S/found.txt
for q in tide low-tide high-tide rain storm river muddy flood sewage drain pipe waves surfer surf rock-beach reef sea-timelapse beach-timelapse; do
  curl -sSL -A "$UA" -m 30 "https://mixkit.co/free-stock-video/$q/" -o /tmp/st/mk_$q.html
  python3 - "$q" /tmp/st/mk_$q.html >> $S/found.txt <<'PY'
import re,sys,html
q,f=sys.argv[1],sys.argv[2]
s=open(f,errors='ignore').read()
seen=set()
for m in re.finditer(r'href="/free-stock-video/([a-z0-9-]+)-(\d+)/"',s):
    t,i=m.group(1),m.group(2)
    if i in seen: continue
    seen.add(i); print(f"mixkit {q} {i} {t}")
PY
done
for q in "tide" "low tide" "high tide" "rain sea" "muddy river sea" "storm drain beach" "river mouth sea" "brown sea water" "surfer riding wave" "closeout wave" "tide timelapse"; do
  qq=$(echo "$q" | sed 's/ /%20/g')
  curl -sSL -A "$UA" -m 30 "https://www.pexels.com/search/videos/$qq/" -o /tmp/st/px.html; echo "pexels $q $(stat -c%s /tmp/st/px.html)" >> $S/found.txt
  grep -o 'https://www.pexels.com/video/[a-z0-9-]*-[0-9]*/' /tmp/st/px.html | sort -u | sed "s|^|pexels $qq |" >> $S/found.txt
  curl -sSL -A "$UA" -m 30 "https://pixabay.com/videos/search/$qq/" -o /tmp/st/pb.html; echo "pixabay $q $(stat -c%s /tmp/st/pb.html)" >> $S/found.txt
  grep -o 'https://cdn.pixabay.com/video/[^"]*_large.mp4\|https://cdn.pixabay.com/video/[^"]*_tiny.mp4' /tmp/st/pb.html | sort -u | sed "s|^|pixabay $qq |" >> $S/found.txt
done
wc -l $S/found.txt; ls -la $O
