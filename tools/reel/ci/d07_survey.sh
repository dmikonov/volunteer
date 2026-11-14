# 07.11 night: HE 10.11 warm-up. Coverr Madeira scene (one man): find cdn mp4 urls from the pages, stills every 1 s.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d07/review; mkdir -p $R /tmp/st out/ci/d07/src
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for p in doing-a-warm-up-before-surfing-hf68pwyk1a stretching-arms-before-surfing-kk2pkhmh8a heading-into-the-sea-ciksmk5qlf man-looking-at-the-sea-n5g9i3znfy man-carrying-a-surfboard-down-the-steps-r41csyqf1t tying-surfboard-leash-to-ankle-k8njhhxphd man-washing-his-surfboard-pmfcwd6ux7 surfer-braving-the-waves-preparation-and-entry-into-the-ocean; do
  curl -sSfL -A "$UA" -m 60 "https://coverr.co/videos/$p" -o /tmp/st/$p.html || echo "PAGEFAIL $p"
  u=$(grep -o 'https://cdn.coverr.co/videos/[^"/?]*/1080p.mp4' /tmp/st/$p.html | head -1)
  [ -z "$u" ] && u=$(grep -o 'cdn.coverr.co/videos/[^"/?\\]*' /tmp/st/$p.html | head -1 | sed 's#^#https://#; s#$#/1080p.mp4#')
  echo "$p $u" >> $R/urls.txt
  grep -o 'cdn.coverr.co/videos/[^"?\\ ]*' /tmp/st/$p.html | sort -u | head -20 >> $R/allurls.txt
done
cat $R/urls.txt
while read p u; do [ -z "$u" ] && continue; n=${p:0:24}
  ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/$n.mp4 "$u" || curl -sSfL -A "$UA" -m 300 -o /tmp/st/$n.mp4 "${u%1080p.mp4}720p.mp4" || echo "FAIL $p"
    cp /tmp/st/$n.mp4 out/ci/d07/src/$n.mp4
    d=$(ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 /tmp/st/$n.mp4 | tr '\n' ' '); echo "$n $d" >> $R/dur.txt
    ffmpeg -nostdin -v error -y -i /tmp/st/$n.mp4 -vf "fps=1,scale=480:-2,drawtext=text='$n %{pts\:hms}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=4x4" -frames:v 1 -q:v 4 $R/sheet_$n.jpg ) &
done < $R/urls.txt; wait
ls -la $R out/ci/d07/src
