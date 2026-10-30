# 02.11 EN chest up when paddling. Real footage: Pexels Kampus Production shoot 81545xx (one man, free licence). One AI shot for the mistake (Z-Image seed 301103 + Wan 2.2).
[ -f /s17/gen/ch_tmrw.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 8155537 8154896 8154903 8154483 8155541; do [ -s /tmp/px/k$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/k$id.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_25fps.mp4; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
ffmpeg -v error -y -i out/ci/d30/gen/ch_err16_raw.mp4 -filter_complex "[0]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.12[bg];[b]scale=1080:-2:flags=lanczos[fg];[bg][fg]overlay=0:(H-h)/2,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/ch_err.mp4
cut k8154483 0.0 2.5 0.36 0.36 ch_fix
cut k8155537 0.3 3.6 0.50 0.55 ch_chest
cut k8154896 0.0 3.6 0.42 0.45 ch_eyes
cut k8154903 3.3 3.8 0.52 0.56 ch_hook
cut k8154903 6.8 3.6 0.55 0.55 ch_deep
cut k8155541 7.0 3.6 0.52 0.52 ch_speed
cut k8154483 5.0 3.2 0.33 0.33 ch_save
ffmpeg -v error -y -ss 22.3 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -frames:v 1 /tmp/en_c.png
ffmpeg -v error -y -loop 1 -t 4 -i /tmp/en_c.png -vf "crop=1080:1920:0:428,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/ch_app.mp4
ffmpeg -v error -y -ss 2.0 -t 4 -i app-screens/ScreenRecording_09-29-2026_13-41-14_1.mp4 -vf "crop=1080:1920:0:240,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/ch_tmrw.mp4
mkdir -p out/ci/d30/review; for f in $G/ch_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d30/review/cut_$n.jpg; done
ls -la $G/ch_*
