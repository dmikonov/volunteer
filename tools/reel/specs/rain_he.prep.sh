# 26.10 rain HE: app insert = week forecast bars (scores per day) from the forecast screen, ~1.06x, no GO/score card (blind viewer 23.10: GO 70 contradicts "don't surf")
set -e
G=/s17/gen; mkdir -p $G
ffmpeg -v error -y -ss 3.0 -t 3.6 -i app-screens/forecast/forecast_he_best.mp4 -filter_complex "\
[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];\
[b]crop=1020:520:30:1090,scale=1080:551:flags=lanczos,unsharp=5:5:0.5[fg];[bg][fg]overlay=0:640,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app_he.mp4
ls -la $G/app_he.mp4
