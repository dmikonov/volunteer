# 01.11 night: tar on feet (HE, 04.11). AI: one man (black wetsuit, striped towel, blue soft board) Z-Image seeds 11043 (hook), 11046 (pour), 11047 (wipe) + Wan 2.2.
# Mixkit free licence: 1064 surfer walking back to the beach, 28889 hourglass, 1013 feet walking on the beach, 1220 surfer walking with board (vertical), 1078 waves on the shore.
[ -f /s17/gen/tr_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d01/review out/ci/d01/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
dl(){ n=$1; u=$2; [ -s out/ci/d01/gen/${n}_raw.mp4 ] || curl -sSfL -m 120 -o out/ci/d01/gen/${n}_raw.mp4 "$u" || echo "FAIL $n"; }
dl tr_hook https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/156b6cc0b521487fd860c97594552a495d6a5e125bea1849b0ca5938f793655e/tmpecs87jym.mp4
dl tr_pour https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/9c2e503e3450aa9a847ac6be3d013168fef8a8701d92fcc0e95e7ea9a429e76f/tmpl3v41k93.mp4
dl tr_wipe https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/dd7e1fd6b958faf73efb4cb5d90f6915dbccfa5451346956d7627a0c2b4d86ad/tmph09u5cvq.mp4
dl tr_gas https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/ca8c8c840ad4fe5b62d37a4eefe58f34f3e140d632763603024ddadf6e769141/tmp0rrau6m5.mp4
for n in tr_hook tr_pour tr_wipe tr_gas; do ffmpeg -v error -y -i out/ci/d01/gen/${n}_raw.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; done
for id in 1064 28889 1013 1078; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m1064 2.0 4.0 0.50 0.50 tr_walk
cut m28889 1.0 4.0 0.50 0.50 tr_wait
cut m1013 3.0 4.0 0.50 0.50 tr_feet
cut m1078 0.0 4.0 0.50 0.50 tr_sea

# app: "שאלו את המאמן" button (HE recording 28.09 15:24 at 11.6 s), big crop over a blurred screen (as flags5 25.10)
ffmpeg -v error -y -ss 11.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/px/he_coach.png
ffmpeg -v error -y -loop 1 -t 4.0 -i /tmp/px/he_coach.png -vf "crop=1080:1180:0:620,pad=1080:1920:0:420:0x2D242A,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/tr_app.mp4
# teaser 05.11: real forecast screen (wave height), as rip3 app_full
ffmpeg -v error -y -ss 1.0 -t 3.0 -i app-screens/forecast/forecast_he_height.mp4 -filter_complex "[0:v]fps=25,crop=1080:1920:0:209,split=2[a][b];[a]boxblur=28,eq=brightness=-0.32[bg];[b]scale=860:-2:flags=lanczos[fg];[bg][fg]overlay=110:520,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/tr_tmrw.mp4
for f in $G/tr_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d01/review/cut_$n.jpg; done
ls -la $G/tr_*
