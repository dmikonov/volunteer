# 24.10 foam4: app inserts = ride replay with skeleton/angles (HE 28.09 15:24 at 17 s; EN 12.10 at 45 s), and the EN teaser set clip
set -e
G=/s17/gen; mkdir -p $G
ffmpeg -v error -y -ss 17 -t 4.2 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.3[bg];[b]crop=1000:1640:40:340,scale=1080:1771:flags=lanczos[fg];[bg][fg]overlay=0:120,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app4_he.mp4
ffmpeg -v error -y -ss 45 -t 4.2 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.3[bg];[b]crop=640:500:220:750,scale=1080:844:flags=lanczos,unsharp=5:5:0.5[fg];[bg][fg]overlay=0:540,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app4_en.mp4
[ -f assets/sets5/st_set1.mp4 ] && ffmpeg -v error -y -t 3.3 -i assets/sets5/st_set1.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/f4_set.mp4
ls -la $G | tail -4
