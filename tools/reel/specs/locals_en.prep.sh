# 04.11 night: new spot and locals (EN, 07.11; plan topic Э08 moved from 16.11, Б10 duplicates "Stop diving" 18.10). Real Mixkit footage (free licence):
# 1127 rider on the peak, 1100/1101/1102 one man with a board (sand, boulders, rocks), 1074 aerial lineup, 1128 small leftover, 1076 aerial clean wave, 1070 aerial wave.
[ -f /s17/gen/lc_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d04b/review
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 1127 1100 1101 1102 1074 1128 1076 1070; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m1074 4.5 4.0 0.50 0.55 lc_hook
cut m1127 4.0 4.5 0.45 0.62 lc_local
cut m1102 1.0 4.0 0.50 0.50 lc_rocks
cut m1101 5.0 5.0 0.18 0.22 lc_watch
# L5: still of the lineup (peak breaking on the left, one surfer waiting on the shoulder) for the PEAK / YOU rings
ffmpeg -v error -y -ss 3.4 -i /tmp/px/m1074.mp4 -frames:v 1 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:(iw-1080)/2:0" /tmp/px/lc_still.png
ffmpeg -v error -y -loop 1 -t 5.0 -i /tmp/px/lc_still.png -vf "fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/lc_aerial.mp4
cut m1128 15.5 4.5 0.45 0.55 lc_left
cut m1076 4.0 4.0 0.50 0.62 lc_ride
cut m1070 6.0 3.0 0.50 0.50 lc_save
cut m1070 11.0 5.0 0.50 0.50 lc_tmrw
# app: EN forecast coach tip: score ring 1.5x + only the tip "Good day means a crowded peak: pick the second-best bank" 2x (no rail-turns line)
ffmpeg -v error -y -ss 2.0 -t 4.0 -i app-screens/forecast/forecast_en_best.mp4 -filter_complex "[0:v]fps=25,split=3[a][b][c];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];[b]crop=340:340:70:640,scale=510:510:flags=lanczos[ring];[c]crop=540:200:450:840,scale=1080:400:flags=lanczos,unsharp=5:5:0.4[tip];[bg][ring]overlay=285:640[t1];[t1][tip]overlay=0:1170,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/lc_app.mp4
for f in $G/lc_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d04b/review/cut_$n.jpg; done
ls -la $G/lc_*
