# foam7 (23.10): all surf shots generated with LTX-2.5 (832x1472, 2-3 s, wide views, board-stays-under-feet prompt); checked at 100% for fins on deck, board slipping, extra limbs; app insert real
set -e
G=/s17/gen; mkdir -p $G
up(){ ffmpeg -v error -y ${3:-} -i assets/gentest/$1.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$2.mp4; }
up ltx25_a ai_hook "-t 1.9"
up ltx2s_ride_s33 ai_ride_side2
up waist2_s51 ai_waist
up ltx_lie_s21 ai_lie
up ride2s_s61 ai_front
up ride2s_s77 ai_ride_side
bash tools/reel/specs/foam5_he.prep.sh
# HE app insert: coach card "מה לשפר" from the 28.09 recording at 8 s (the replay at 17 s shows the C0120 surfer, banned)
ffmpeg -v error -y -ss 8 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/he8.png
ffmpeg -v error -y -loop 1 -t 4.5 -i /tmp/he8.png -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.3[bg];[b]crop=960:330:80:1290,scale=1040:-2:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=20:760,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/app4_he.mp4
