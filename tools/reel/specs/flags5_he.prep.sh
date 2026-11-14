# 25.10 flags5 HE / sets5 EN: app inserts (HE: "שאלו את המאמן" button, freeze at 11.6 s of 28.09 15:24; EN: "Where you rode the wave" card, 12.10 at 27.3 s), EN stock masters (Pexels/Mixkit free licences, sets5 Wan clips)
set -e
G=/s17/gen; mkdir -p $G /tmp/st
ffmpeg -v error -y -ss 11.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/st/he_coach.png
ffmpeg -v error -y -loop 1 -t 3.5 -i /tmp/st/he_coach.png -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.3[bg];[b]crop=1000:420:40:1400,scale=1080:454:flags=lanczos[fg];[bg][fg]overlay=0:760,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/app5_he.mp4
ffmpeg -v error -y -ss 27.3 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -frames:v 1 /tmp/st/en_where.png
ffmpeg -v error -y -loop 1 -t 4 -i /tmp/st/en_where.png -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.3[bg];[b]crop=960:440:60:910,scale=1080:495:flags=lanczos[fg];[bg][fg]overlay=0:740,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/app5_en.mp4
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
g(){ [ -f /tmp/st/$1.mp4 ] || curl -sSfL -A "$UA" --connect-timeout 15 -m 240 -o /tmp/st/$1.mp4 "$2" || echo "FAIL $1"; }
v(){ ffmpeg -nostdin -v error -y -ss $3 -t $4 -i /tmp/st/$2.mp4 -vf "crop=ih*9/16:ih:max(0\,min(iw-ih*9/16\,iw*$5-ih*9/32)):0,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 -preset medium $G/$1.mp4; }
g p15547520 https://videos.pexels.com/video-files/15547520/15547520-uhd_2560_1440_60fps.mp4; v st_big p15547520 2 6 0.5
g m38939 https://assets.mixkit.co/videos/38939/38939-1080.mp4; v st_m38939 m38939 0 15 0.5
g m1076 https://assets.mixkit.co/videos/1076/1076-1080.mp4; v st_m1076 m1076 0 18 0.55
g m1163 https://assets.mixkit.co/videos/1163/1163-1080.mp4; v st_m1163 m1163 0 26 0.6
for n in st_set1 st_lineup; do ffmpeg -v error -y -i assets/sets5/$n.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/${n/st_lineup/st_lineup5}.mp4; done
ls -la $G | tail -12
