# 26.10 rain HE: app insert = forecast "best" screen (coach tip with best hour + week forecast), crop ~1.06x over blurred bg
set -e
G=/s17/gen; mkdir -p $G
for L in he en; do
ffmpeg -v error -y -ss 2.0 -t 3.8 -i app-screens/forecast/forecast_${L}_best.mp4 -filter_complex "\
[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];\
[b]crop=1020:1110:30:390,scale=1080:1175:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:540,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app_$L.mp4
done
ls -la $G | tail -3
