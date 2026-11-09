# 10.11 night: 13.11 HE thunder (Б21). Real: Mixkit 4059 (lightning over the horizon), 48854 (storm promenade), 9624 (storm sky timelapse), 17969 (gulls under storm clouds), Pexels 8713107 (drone shore break).
# AI (Z-Image Turbo seeds 111006/111008/111002/111004 + Wan 2.2): th_sit (man on board, lightning), th_paddle (same look, paddling), th_shelter (beach shelter + lamp post), th_car (from the driver's seat, lightning over the sea; wheel emblem cropped out).
G=/s17/gen; S=out/ci/d10/src; W=out/ci/d10/gen; R=out/ci/d10/review; mkdir -p $G $R /tmp/px
[ -f $G/th_look_c.mp4 ] && exit 0
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
[ -s /tmp/px/m4059.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/m4059.mp4 https://assets.mixkit.co/videos/4059/4059-720.mp4
cp /tmp/px/m4059.mp4 $S/ 2>/dev/null
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m4059 0.0 3.4 0.50 0.50 th_hook
cut m48854 2.0 3.0 0.50 0.55 th_prom
cut m9624 4.0 4.0 0.50 0.50 th_sky
cut m17969 2.0 5.0 0.45 0.50 th_save
cut p8713107 1.5 5.0 0.50 0.50 th_tmrw
gen(){ n=$1; vf=$2; o=${3:-${1}_c}; ffmpeg -v error -y -i $W/$n.mp4 -vf "$vf,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$o.mp4; }
# 10.11 r2: Wan keeps the lightning bolt frozen for 3.5 s (looks fake). Hide it under a soft blur and let it flash twice (0.1-0.2 s) with a sky flash.
flash(){ n=$1; bx=$2; by=$3; bw=$4; bh=$5; t1=$6; t2=$7; post=$8
  ffmpeg -v error -y -i $W/$n.mp4 -filter_complex "[0:v]split[a][b];[b]crop=iw*$bw:ih*$bh:iw*$bx:ih*$by,boxblur=18:3[bl];[a][bl]overlay=W*$bx:H*$by:enable='not(between(t,$t1,$t1+0.14)+between(t,$t2,$t2+0.2))',eq=brightness='0.10*(between(t,$t1,$t1+0.14)+between(t,$t2,$t2+0.2))':eval=frame,$post,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 15 $G/${n}_c.mp4; }
flash th_sit 0.36 0.22 0.28 0.24 0.0 1.45 "crop=iw:ih:0:0"
flash th_paddle 0.31 0.20 0.27 0.24 0.35 1.7 "crop=iw:ih:0:0"
flash th_car 0.35 0.28 0.25 0.23 0.3 1.25 "crop=iw*0.86:ih*0.86:iw*0.07:0"
gen th_shelter2 "crop=iw:ih:0:0" th_shelter_c
gen th_look "crop=iw*0.78:ih*0.78:iw*0.11:0"
ffmpeg -v error -y -ss 2.0 -t 4.2 -i app-screens/forecast/forecast_he_best.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];[b]crop=600:450:365:1150,scale=1080:810:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:660,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/th_app.mp4
for f in $G/th_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/th_*
