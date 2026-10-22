# rip v3: vertical masters from chosen stock (Pexels licence, free commercial use)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
O=out/ci/rip3/gen; R=out/ci/rip3/review; mkdir -p $O $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
g(){ curl -sSfL -A "$UA" --connect-timeout 15 -m 240 -o /tmp/st/$1.mp4 "$2"; }
g p38005980 https://videos.pexels.com/video-files/38005980/16129499_2560_1440_60fps.mp4
g p31663047 https://videos.pexels.com/video-files/31663047/13490837_2560_1440_30fps.mp4
g p8713107 https://videos.pexels.com/video-files/8713107/8713107-hd_1080_1920_25fps.mp4
# beach on the left in the source -> rotate 90 ccw: beach at the bottom, open sea at the top
ffmpeg -nostdin -v error -y -t 7 -i /tmp/st/p38005980.mp4 -vf "transpose=2,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 -preset medium $O/st_rip1.mp4
ffmpeg -nostdin -v error -y -i /tmp/st/p31663047.mp4 -vf "transpose=2,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 -preset medium $O/st_rip2.mp4
ffmpeg -nostdin -v error -y -i /tmp/st/p8713107.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 -preset medium $O/st_rip3.mp4
for n in st_rip1 st_rip2 st_rip3; do ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=2,scale=360:-2,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.5,tile=7x2" -frames:v 1 $R/${n}_sheet.jpg; done
for t in 0 2 4 6; do ffmpeg -nostdin -v error -y -ss $t -i $O/st_rip1.mp4 -frames:v 1 -q:v 3 $R/st_rip1_$t.jpg; done
ls -la $O $R
