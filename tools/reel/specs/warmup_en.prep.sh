# 05.11 night: EN 08.11 "5-minute warm-up" (Ф01, moved from 10.11; Т108 pop-up has no stock). Real footage only (Pexels free licence):
# hero on the sand = one man (short hair, all-black wetsuit) from the Pexels 62996xx shoot: 6299679 side lunge, 6299684 side plank, 6299681 upward dog (crops keep the kids out).
# water = Pexels Kampus Production 81545xx paddler: 8154903 and 8154896 struggling/splashing (problem), 8155541 smooth paddle (payoff), 8154896 start for the teaser.
# app: "Training until next session" land drills, EN recording 26.09 (18.0 s).
[ -f /s17/gen/wu_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d05w/cuts
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 6299679 6299681 6299684; do [ -s /tmp/px/p$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p$id.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_25fps.mp4 || echo "FAIL $id"; done
for id in 8154903 8154896 8155541; do [ -s /tmp/px/k$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/k$id.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_25fps.mp4 || echo "FAIL $id"; done
# cutz src ss t cx0 cx1 H cy n : scale to height H, crop 1080x1920 centred on x fraction cx (pan cx0->cx1), top = cy fraction of the scaled height minus 960
cutz(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; H=$6; cy=$7; n=$8
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:$H:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':'max(0,min(ih-1920,$cy*ih-960))',fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cutz k8154903 3.3 2.8 0.52 0.55 1920 0.5 wu_hook
cutz k8154896 4.0 3.0 0.45 0.45 1920 0.5 wu_tired
cutz p6299684 0.0 2.4 0.66 0.66 2880 0.60 wu_three
cutz p6299679 0.5 3.4 0.36 0.36 1920 0.5 wu_lunge
cutz p6299681 1.0 3.2 0.70 0.70 2880 0.58 wu_dog
cutz p6299684 4.0 3.2 0.69 0.69 2880 0.60 wu_plank
cutz k8155541 10.0 3.4 0.50 0.50 1920 0.5 wu_glide
cutz k8155541 13.4 3.2 0.50 0.50 1920 0.5 wu_save
cutz k8154896 0.0 3.4 0.42 0.45 1920 0.5 wu_tmrw
# app: land drills ("Flat-land pump reps" + "Land and freeze") from the 26.09 EN analysis, 1.35x over the blurred screen: insert 1080x972 (51% of the frame)
ffmpeg -v error -y -ss 18.0 -i app-screens/ScreenRecording_09-26-2026_17-24-44_1.mp4 -frames:v 1 /tmp/px/drills.png
ffmpeg -v error -y -loop 1 -t 4.0 -i /tmp/px/drills.png -filter_complex "[0:v]split=2[a][b];[a]crop=1080:1920:0:214,boxblur=28,eq=brightness=-0.3[bg];[b]crop=800:720:140:430,scale=1080:972:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:600,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/wu_app.mp4
for f in $G/wu_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d05w/cuts/cut_$n.jpg; done
ls -la $G/wu_*
