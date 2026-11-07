# 08.11 night: 11.11 "count sets" (М05) HE+EN. Real Mixkit footage (free licence), one session at one beach (389xx: 38939 lineup at sunset,
# 38927 rider, 38933 whitewater toward the beach) + 1071 (aerial: whitewater over paddlers) + SurfTribe forecast "period" tile.
G=/s17/gen; R=out/ci/d08/review; S=out/ci/d08/src; mkdir -p $G $R
[ -f $G/st_tmrw.mp4 ] || {
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m38939 0.0 4.0 0.40 0.44 st_hook
cut m1071  4.0 4.0 0.55 0.55 st_hit
cut m38933 14.5 4.5 0.45 0.45 st_bridge
cut m38939 9.8 4.6 0.42 0.42 st_count
cut m38933 0.3 4.2 0.48 0.44 st_lull
cut m38927 0.0 4.0 0.30 0.42 st_last
cut m38933 8.5 4.0 0.50 0.50 st_back
cut m38927 5.5 4.5 0.42 0.38 st_save
cut m38939 4.8 3.6 0.38 0.40 st_tmrw
}
app(){ l=$1; x=$2; y=$3; w=$4; h=$5; s=$6; n=$7
  W2=$(python3 -c "print(int($w*$s)//2*2)"); H2=$(python3 -c "print(int($h*$s)//2*2)"); X=$(( (1080-W2)/2 ))
  ffmpeg -v error -y -ss 3.6 -t 2.9 -i app-screens/forecast/forecast_${l}_period.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.30[bg];[b]crop=$w:$h:$x:$y,scale=$W2:$H2:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=$X:430,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/$n.mp4; }
[ -f $G/st_app_he.mp4 ] || app he 676 876 296 398 2.5 st_app_he
[ -f $G/st_app_en.mp4 ] || app en 112 870 296 398 2.5 st_app_en
for f in $G/st_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/st_*
