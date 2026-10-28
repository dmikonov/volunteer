# 28.10 drop (don't let the wave throw your board): real Pexels footage only (free licence), 1440p originals cropped to 9:16 here.
# Same man (grey beard, red soft top, Pexels 7938xxx series) in hook, mistake, carry, walk-out. Technique shots (nose over the foam) are another surfer (7425578): no clip of the same man doing it.
[ -f /s17/gen/dr_hook.mp4 ] && exit 0
set -e
G=/s17/gen; mkdir -p $G /tmp/px
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 7938440 7938113 7938106 7425578 7425581 7938443 7938442 7938446; do u=$(cat out/ci/d28/review/resolved.txt out/ci/d29/review/resolved.txt | grep "^$id " | head -1 | cut -d' ' -f2); [ -s /tmp/px/$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/$id.mp4 "$u" || cp out/ci/d28/src/p$id.mp4 /tmp/px/$id.mp4; done
cut(){ id=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$id.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut 7938440 8.55 2.33 0.55 0.55 dr_hook
cut 7938440 0.0 2.3 0.50 0.50 dr_hit2
cut 7425581 5.0 3.4 0.55 0.55 dr_wipe
cut 7938113 0.0 2.8 0.40 0.42 dr_carry
cut 7938113 5.2 3.1 0.36 0.36 dr_side
cut 7938440 3.0 3.6 0.50 0.50 dr_across
cut 7425578 2.0 2.4 0.20 0.28 dr_side2
cut 7425578 5.6 2.0 0.25 0.38 dr_walk
cut 7425578 7.6 2.3 0.55 0.64 dr_over
cut 7938442 6.8 2.0 0.50 0.52 dr_hit3
cut 7938442 9.6 2.5 0.50 0.45 dr_lie
cut 7938446 0.0 4.0 0.55 0.55 dr_paddle2
cut 7425578 10.3 1.5 0.52 0.47 dr_past
cut 7938443 1.0 5.0 0.45 0.45 dr_paddle
cut 7938106 3.0 4.5 0.45 0.45 dr_out
cut 7425581 0.0 2.8 0.60 0.60 dr_tmrw
cut 7425581 2.8 2.2 0.60 0.60 dr_tmrw2
# app: "Ask the coach" (EN 12.10 recording 22.3 s, HE 28.09 recording 11.45 s). Shot 1: real screen part, full width, below the title. Shot 2: the button 1.37x (text over 44 px).
ffmpeg -v error -y -ss 22.3 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -frames:v 1 /tmp/en_c.png
ffmpeg -v error -y -ss 11.45 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/he_c.png
app(){ L=$1; y0=$2; h=$3; by=$4
ffmpeg -v error -y -loop 1 -t 3 -i /tmp/${L}_c.png -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.35[bg];[b]crop=1080:$h:0:$y0[fg];[bg][fg]overlay=0:620,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/dr_appfull_$L.mp4
ffmpeg -v error -y -loop 1 -t 3 -i /tmp/${L}_c.png -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:200,boxblur=28,eq=brightness=-0.35[bg];[b]crop=760:170:160:$by,scale=1040:-2:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=20:860,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/dr_appbtn_$L.mp4; }
app en 760 1240 1600
app he 1100 995 1735
mkdir -p out/ci/d28/review; for f in $G/dr_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=12x1" -frames:v 1 out/ci/d28/review/cut_$n.jpg; done
ls -la $G
