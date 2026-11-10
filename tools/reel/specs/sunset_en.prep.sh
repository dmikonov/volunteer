# 10.11 night: 13.11 EN sunset session (Б18). Real only: Mixkit 6892 (surfers at sunset, one session), 38901 (surfing near the shore at sunset), 1128 (rider on a green face), Pexels 8713110/8713111 (man at his car at dusk). App: forecast_en_best (coach tip "best ~06:00").
G=/s17/gen; S=out/ci/d10/src; R=out/ci/d10/review; mkdir -p $G $R /tmp/px
[ -f $G/en_tmrw.mp4 ] && [ -f $G/en_r2 ] && exit 0
touch $G/en_r2
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 6892 38901 1128; do [ -s $S/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o $S/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m6892 0.8 3.6 0.48 0.52 en_hook
cut m6892 12.0 3.4 0.45 0.50 en_dark
cut m38901 2.0 3.0 0.50 0.50 en_bridge
cutz(){ src=$1; ss=$2; t=$3; H=$4; cx=$5; cy=$6; n=$7
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:$H:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,$cx*iw-540))':'max(0,min(ih-1920,$cy*ih-960))',fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cutz m6892 4.0 3.6 2400 0.50 0.50 en_sun
cutz m6892 9.0 3.0 2880 0.56 0.62 en_buddy
cut m6892 14.5 3.4 0.50 0.50 en_set
cut p8713111 4.6 4.4 0.50 0.50 en_car
cut p8713110 0.0 5.0 0.50 0.50 en_save
cut m1128 4.0 4.5 0.40 0.60 en_tmrw
ffmpeg -v error -y -ss 1.5 -t 4.0 -i app-screens/forecast/forecast_en_best.mp4 -filter_complex "[0:v]fps=25,scale=1080:-2,split=2[a][b];[a]crop=1080:1920:0:0,boxblur=28,eq=brightness=-0.28[bg];[b]crop=620:470:430:530,scale=1080:819:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:600,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/en_app.mp4
for f in $G/en_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/en_*
