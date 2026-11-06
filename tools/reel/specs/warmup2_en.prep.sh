# 07.11 night: EN 10.11 warm-up v2 on the same Coverr Madeira man as warmup_he (clips wm_* made by warmup_he.prep.sh, run it first).
# app: Ask the coach button, EN recording 12.10 (22.5 s), as locals_en.
bash tools/reel/specs/warmup_he.prep.sh
[ -f /s17/gen/we_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p /tmp/px
ffmpeg -v error -y -ss 22.5 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -frames:v 1 /tmp/px/ask.png
ffmpeg -v error -y -ss 11.0 -t 3.6 -i /tmp/px/man-washing-his-surfboar.mp4 -loop 1 -i /tmp/px/ask.png -filter_complex "[0:v]scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,0.45*iw-540))':0[bg];[1:v]crop=864:420:108:1560,scale=1080:525:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:900:shortest=1,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/we_app.mp4
ffmpeg -v error -y -i /tmp/px/ask.png -vf "crop=864:420:108:1560" out/ci/d07/review/ask_crop.jpg
ls -la $G/we_app.mp4
