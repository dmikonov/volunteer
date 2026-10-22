# 23.10 rip v3: app insert (forecast height screen, crop of wave height + wind tiles, ~1.29x), both languages
set -e
G=/s17/gen; mkdir -p $G
for L in en he; do
ffmpeg -v error -y -ss 3.0 -t 3.6 -i app-screens/forecast/forecast_${L}_height.mp4 -filter_complex "\
[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];\
[b]crop=840:760:120:500,scale=1080:977:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:470,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app_$L.mp4
done
ls -la $G
