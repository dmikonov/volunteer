# D+3 26.10: vertical 1080x1920 masters from chosen stock (Pexels / Mixkit free licences) + F5 takes
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/d26/gen; R=out/ci/d26/review; T=out/ci/d26/takes; mkdir -p $O $R $T /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
g(){ curl -sSfL -A "$UA" --connect-timeout 15 -m 240 -o /tmp/st/$1.mp4 "$2" || echo "FAIL $1"; }
g p13831212 https://videos.pexels.com/video-files/13831212/13831212-uhd_2560_1440_60fps.mp4 &
g p7498300 https://videos.pexels.com/video-files/7498300/7498300-uhd_2560_1440_30fps.mp4 &
g p4961454 https://videos.pexels.com/video-files/4961454/4961454-uhd_2560_1440_30fps.mp4 &
g m1070 https://assets.mixkit.co/videos/1070/1070-1080.mp4 &
g m38933 https://assets.mixkit.co/videos/38933/38933-1080.mp4 &
g m26310 https://assets.mixkit.co/videos/26310/26310-720.mp4 &
g m1128 https://assets.mixkit.co/videos/1128/1128-1080.mp4 &
g m36833 https://assets.mixkit.co/videos/36833/36833-720.mp4 &
g m1904 https://assets.mixkit.co/videos/1904/1904-1080.mp4 &
wait
# v <name> <src> <start> <dur> <crop-centre-x 0..1>
v(){ ffmpeg -nostdin -v error -y -ss $3 -t $4 -i /tmp/st/$2.mp4 -vf "crop=ih*9/16:ih:max(0\,min(iw-ih*9/16\,iw*$5-ih*9/32)):0,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 -preset medium $O/$1.mp4
  ffmpeg -nostdin -v error -y -i $O/$1.mp4 -vf "fps=2,scale=270:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.5,tile=8x2" -frames:v 1 $R/${1}_sheet.jpg; }
v st_river p13831212 12 11 0.6
v st_lineup p7498300 0 7.3 0.5
v st_soft p4961454 0 9 0.45
v st_close m1070 4 10 0.5
v st_dump m38933 0 7 0.5
v st_tide m26310 0 10.5 0.5
v st_ride m1128 1 9 0.58
v st_ride2 m36833 4 11 0.68
v st_rocks m1904 0 8 0.4
while read i s u; do [ -z "$i" ] && continue; f=$T/L$((i+1))_s$s.wav; [ -f $f ] && continue; curl -sSfL --retry 3 -o $f "$u" || echo "FAIL $f"; done < tools/reel/ci/d26_takes_list.txt
ls -la $O $R $T
