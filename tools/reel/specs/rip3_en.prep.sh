# 23.10 rip v3: app insert (forecast height screen, crop of wave height + wind tiles, ~1.29x), both languages
set -e
G=/s17/gen; mkdir -p $G
for L in en he; do
ffmpeg -v error -y -ss 3.0 -t 3.6 -i app-screens/forecast/forecast_${L}_height.mp4 -filter_complex "\
[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];\
[b]crop=840:760:120:500,scale=1080:977:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:470,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium $G/app_$L.mp4
done
ls -la $G
[ -f /s17/gen/r3_arm2.mp4 ] || { echo "ARM2 MISSING, fallback r3_arm"; cp /s17/gen/r3_arm.mp4 /s17/gen/r3_arm2.mp4; }
# r6: big surf for "when the swell's up" (Pexels 33731641, David Pickup, Fistral), 13.0-16.0 s, centre 9:16
curl -sSfL -A "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0" --connect-timeout 15 -m 180 -o /tmp/p33731641.mp4 https://videos.pexels.com/video-files/33731641/14322457_2560_1440_30fps.mp4 && \
ffmpeg -v error -y -ss 13.0 -t 3.0 -i /tmp/p33731641.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 /s17/gen/st_big.mp4 || { echo "BIG SURF MISSING, fallback st_rip3"; cp /s17/gen/st_rip3.mp4 /s17/gen/st_big.mp4; }
mkdir -p out/ci/rip3/review && ffmpeg -v error -y -i /s17/gen/st_big.mp4 -vf "fps=2,scale=270:-2,tile=6x1" -frames:v 1 out/ci/rip3/review/st_big_sheet.jpg || true
# 23.10 Dima: real app screen before the wave-height card (line "check wave height in the SurfTribe app")
for L in en he; do ffmpeg -v error -y -ss 1.0 -t 2.2 -i app-screens/forecast/forecast_${L}_height.mp4 -filter_complex "[0:v]fps=25,crop=1080:1920:0:209,split=2[a][b];[a]boxblur=28,eq=brightness=-0.32[bg];[b]scale=760:-2:flags=lanczos[fg];[bg][fg]overlay=160:500,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 /s17/gen/app_${L}_full.mp4 || cp /s17/gen/app_${L}_card.mp4 /s17/gen/app_${L}_full.mp4; done
