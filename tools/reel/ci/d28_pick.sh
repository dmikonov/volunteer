# 28.10: keep chosen Pexels clips at 1080p (src), 4 fps sheets at 360 px for close review
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
S=out/ci/d28/src; R=out/ci/d28/review; mkdir -p $S $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 7938440 7425578 7938113 7938106 7425581 7938443 8713112 7938112; do u=$(grep "^$id " $R/resolved.txt | cut -d' ' -f2)
 ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/$id.mp4 "$u" && \
   ffmpeg -nostdin -v error -y -i /tmp/st/$id.mp4 -vf "scale=-2:1080:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 18 -preset fast $S/p$id.mp4 && \
   ffmpeg -nostdin -v error -y -i $S/p$id.mp4 -vf "fps=4,scale=-2:300,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=6x8" $R/p${id}_z%02d.jpg ) &
done; wait; ls -la $S $R | tail -40
