# 05.11 night: HE 05.11 "how to read a forecast" (period, wind, height). All real Mixkit footage (free licence) + SurfTribe forecast screen (HE recording 19.10).
# 20889 messy wind sea at a city beach, 48824 choppy grey sea, 48525 aerial clean lines, 5016 small waves on sand, 1075 surfer on a wave, 1032 surfer running on the beach.
[ -f /s17/gen/fc_app_h.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d05f/review out/ci/d05f/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 20889 48824 48525 5016 1075 1032; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 /tmp/px/m$id.mp4 > out/ci/d05f/review/m${id}_info.txt; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
half(){ src=$1; ss=$2; t=$3; c=$4; o=$5
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:960:flags=lanczos,crop=1080:960:'max(0,min(iw-1080,$c*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $o; }
cut m20889 0.0 5.8 0.62 0.70 fc_hook
half m48824 1.0 4.0 0.5 /tmp/px/top.mp4
half m48525 2.0 4.0 0.5 /tmp/px/bot.mp4
ffmpeg -v error -y -i /tmp/px/top.mp4 -i /tmp/px/bot.mp4 -filter_complex "[0:v][1:v]vstack=2,drawbox=x=0:y=956:w=1080:h=8:color=white@0.9:t=fill,format=yuv420p" -an -c:v libx264 -crf 15 $G/fc_split.mp4
cut m48525 6.5 3.0 0.45 0.55 fc_lines
cut m48824 5.0 3.0 0.50 0.50 fc_chop
cut m5016 1.0 3.0 0.40 0.45 fc_small
cut m1075 0.0 6.0 0.50 0.50 fc_ride
cut m1032 2.0 4.0 0.50 0.50 fc_tmrw
# app inserts: one tile of the HE forecast screen, x2.2-2.4 over the blurred screen (insert about 600x850, centre band y 560-1420)
app(){ f=$1; x=$2; y=$3; w=$4; h=$5; s=$6; n=$7
  W2=$(python3 -c "print(int($w*$s)//2*2)"); H2=$(python3 -c "print(int($h*$s)//2*2)"); X=$(( (1080-W2)/2 ))
  ffmpeg -v error -y -ss 4.2 -t 2.3 -i app-screens/forecast/forecast_he_$f.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.30[bg];[b]crop=$w:$h:$x:$y,scale=$W2:$H2:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=$X:560,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/$n.mp4; }
app period 680 870 290 400 2.1 fc_app_p
app period 136 896 244 348 2.4 fc_app_w
app height 530 490 440 410 2.0 fc_app_h
# bridge: the whole forecast screen (score, weekly bars)
ffmpeg -v error -y -ss 0.3 -t 3.5 -i app-screens/forecast/forecast_he_best.mp4 -vf "fps=25,crop=1080:1920:0:209,format=yuv420p" -an -c:v libx264 -crf 14 $G/fc_app_all.mp4
for f in $G/fc_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d05f/review/cut_$n.jpg; done
ls -la $G/fc_*
