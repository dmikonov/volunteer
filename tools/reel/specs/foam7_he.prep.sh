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
