# 28.10 carousel: full-res stills (1440p originals, Pexels free licence) for the "board" carousel
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/c28/stills; mkdir -p $O /tmp/px
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 7938440 7938113 7425578 7938442 7938446 7938106; do u=$(cat out/ci/d28/review/resolved.txt out/ci/d29/review/resolved.txt | grep "^$id " | head -1 | cut -d' ' -f2); curl -sSfL -A "$UA" -m 300 -o /tmp/px/$id.mp4 "$u" || echo FAIL $id; done
st(){ ffmpeg -v error -y -ss $2 -i /tmp/px/$1.mp4 -frames:v 1 -q:v 2 $O/$1_$2.jpg; }
for t in 9.2 9.4 9.6 9.8 10.0 4.0 5.0; do st 7938440 $t; done
for t in 5.5 6.5 7.5; do st 7938113 $t; done
for t in 8.8 9.0 9.2 9.4 9.6; do st 7425578 $t; done
for t in 7.4 7.8 10.4 10.9 11.4; do st 7938442 $t; done
for t in 1.0 2.0 3.0 4.0; do st 7938446 $t; done
for t in 3.5 5.0; do st 7938106 $t; done
ls -la $O
