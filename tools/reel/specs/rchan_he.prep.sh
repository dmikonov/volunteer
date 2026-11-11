# 12.11 night: 15.11 "rip as a paddle-out channel" (Т301), HE+EN share cuts. Real footage only:
# Pexels 15317073 (reef, surfer sits in calm water next to the break), 6989125 (reef point, channel), 31845098 (Bondi, Macourt Media),
# 7498300 (lineup), 10540776 (shore top-down), Mixkit 36924 (sunset ride), 1075 (grey surf); st_rip2 (rip3, Pexels 31663047 plume).
G=/s17/gen; S=out/ci/d12/src; R=out/ci/d12/review; mkdir -p $G $R
[ -f $G/rc_tmrw_en.mp4 ] && exit 0
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cutz(){ src=$1; ss=$2; t=$3; cx=$4; cy=$5; z=$6; n=$7
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:$z:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,$cx*iw-540))':'max(0,min(ih-1920,$cy*ih-960))',fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut p15317073 0.0 4.4 0.66 0.62 rc_side
cutz p6989125 13.5 2.4 0.62 0.62 3000 rc_out
cutz p31845098 12.5 3.6 0.45 0.55 2400 rc_big
cut p31845098 9.0 4.0 0.40 0.44 rc_gap
cut p6989125 8.0 4.0 0.50 0.58 rc_hook
cut p7498300 2.0 5.0 0.45 0.52 rc_lineup
cut p10540776 0.5 5.5 0.45 0.50 rc_par
cut m36924 2.0 5.0 0.50 0.56 rc_save
cut m1075 0.0 4.4 0.40 0.45 rc_appbg
cut m1075 9.0 4.4 0.45 0.50 rc_tmrw_he
cut m36924 18.0 4.4 0.50 0.56 rc_tmrw_en
# app: wave height tile, big, over the same grey surf (lesson 08.11: never on black)
for L in he en; do X=556; [ $L = en ] && X=136
  ffmpeg -v error -y -i $G/rc_appbg.mp4 -ss 3.0 -i app-screens/forecast/forecast_${L}_height.mp4 -filter_complex "[1:v]crop=384:316:$X:544,scale=845:695:flags=lanczos,unsharp=5:5:0.4,fps=25[fg];[0:v][fg]overlay=117:640:shortest=1,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/rc_app_$L.mp4
done
for f in $G/rc_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/rc_*
