# 26.10 tide EN: app insert = forecast tiles (wave height, period, swell, wind), ~1.12x; soft-wave stock (Mixkit 38939, free licence)
set -e
G=/s17/gen; mkdir -p $G /tmp/st
ffmpeg -v error -y -ss 3.0 -t 3.6 -i app-screens/forecast/forecast_en_height.mp4 -filter_complex "\
[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];\
[b]crop=960:1080:60:600,scale=1080:1215:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:420,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app_en.mp4
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
curl -sSfL -A "$UA" -m 240 -o /tmp/st/m38939.mp4 https://assets.mixkit.co/videos/38939/38939-1080.mp4
ffmpeg -nostdin -v error -y -ss 5 -t 7 -i /tmp/st/m38939.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 $G/st_soft2.mp4
ls -la $G/app_en.mp4 $G/st_soft2.mp4
