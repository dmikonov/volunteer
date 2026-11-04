# 31.10 night: EN "Stop splashing" (Т109). Real stock, one man in every beat: Pexels Kampus Production 8154903, 8155537, 8155548, 8154486, 8154896, 8155541 (free licence).
# App: Ask the coach button, EN recording 12.10 (22.0 s).
[ -f /s17/gen/sp_hook.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d31s/review
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 8154903 8155537 8155548 8154486 8154896 8155541; do [ -s /tmp/px/k$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/k$id.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_25fps.mp4 || echo "FAIL $id"; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut k8154903 7.3 2.2 0.42 0.42 sp_hook
cut k8154903 0.5 2.2 0.50 0.50 sp_slap
cut k8155537 0.0 2.0 0.50 0.50 sp_three
cut k8155537 1.5 2.4 0.58 0.58 sp_tips
cut k8155548 8.8 2.6 0.55 0.58 sp_pull
cut k8154486 2.5 3.5 0.50 0.50 sp_long
cut k8154486 18.0 4.0 0.58 0.62 sp_glide
cut k8154896 4.0 3.2 0.45 0.45 sp_save
cut k8155541 10.0 3.2 0.50 0.50 sp_tmrw
ffmpeg -v error -y -ss 22.0 -t 2.4 -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -vf "crop=864:1536:108:450,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/sp_coach.mp4
for f in $G/sp_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d31s/review/cut_$n.jpg; done
ls -la $G/sp_*
