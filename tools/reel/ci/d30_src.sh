# 30.10: sources for film_he (Pexels 4782364/4782485 Taryn Elliott Waikiki series, Mixkit) and chest_en (Mixkit 1042 one woman paddling) + Wan filmer clip. Sheets 4 fps, 480 px.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
bash tools/reel/ci/d30_takes.sh
R=out/ci/d30/src; mkdir -p $R /tmp/st out/ci/d30/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
curl -sSfL -m 120 -o out/ci/d30/gen/fm_film_raw.mp4 "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/bwlzl/gradio_api/file=/tmp/gradio/909cc88907d15acdfc361bd64fe2636ca7c1555a4e3d8afc2bbd656c95a17a61/tmpqtockgzb.mp4" || echo FAIL wan
for x in p4782364 p4782485; do id=${x#p}; curl -sSfL -A "$UA" -m 300 -o /tmp/st/$x.mp4 https://videos.pexels.com/video-files/$id/$id-uhd_2560_1440_30fps.mp4 || echo FAIL $x; done
for id in 15845 1069 1220 1100 1042 15727 1580 1578 21286; do for q in 1080 720; do curl -sSfL -A "$UA" -m 200 -o /tmp/st/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
for f in /tmp/st/*.mp4 out/ci/d30/gen/fm_film_raw.mp4; do n=$(basename $f .mp4); ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/${n}_info.txt
 ffmpeg -nostdin -v error -y -i $f -vf "fps=4,scale=-2:300,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x6" -frames:v 1 $R/${n}_sheet.jpg & done; wait
# full-res frames of the wide Waikiki shot to find a tiny surfer
for t in 1 4 7 10; do ffmpeg -nostdin -v error -y -ss $t -i /tmp/st/p4782364.mp4 -frames:v 1 -q:v 2 $R/p4782364_full_$t.jpg; done
for t in 1 3; do ffmpeg -nostdin -v error -y -ss $t -i /tmp/st/p4782485.mp4 -frames:v 1 -q:v 2 $R/p4782485_full_$t.jpg; done
for t in 1 6 12 16 19; do ffmpeg -nostdin -v error -y -ss $t -i /tmp/st/m1042.mp4 -frames:v 1 -q:v 2 $R/m1042_full_$t.jpg; done
ls -la $R out/ci/d30/gen
