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
dl tr_oil https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/322a3f4602ff647ec686e3778c812503f20ebb2a36852f51ede3af23f2b14cc4/tmpup5ilwmx.mp4
dl tr_clean https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/97f2d797e3ba81f67edf5a4ce2700dac38b6a2e6bb2297dd0ae249bb1f3ba1df/tmpdt_e58a2.mp4
dl tr_red https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/clg9g/gradio_api/file=/tmp/gradio/10d3d5d6cf0bfc96ae6544d00344e98b1ffd63bf5a86ddca69b071413571a321/tmpsrfje763.mp4
for n in tr_hook tr_pour tr_wipe tr_gas tr_oil tr_red tr_clean; do ffmpeg -v error -y -i out/ci/d01/gen/${n}_raw.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; done
for id in 1064 28889 1013 1078; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m1064 1.0 4.8 0.50 0.50 tr_walk
cut m28889 1.0 4.0 0.50 0.50 tr_wait
cut m1013 3.0 4.0 0.50 0.50 tr_feet
cut m1078 0.0 4.0 0.50 0.50 tr_sea

# app: "שאלו את המאמן" button (HE recording 28.09 15:24 at 11.6 s), big crop over a blurred screen (as flags5 25.10)
ffmpeg -v error -y -ss 11.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/px/he_coach.png
ffmpeg -v error -y -i $G/tr_walk.mp4 -loop 1 -i /tmp/px/he_coach.png -filter_complex "[1:v]crop=960:200:60:1460,scale=1080:225:flags=lanczos[fg];[0:v][fg]overlay=0:1080:shortest=1,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/tr_app.mp4
# teaser 05.11: real forecast screen (wave height), as rip3 app_full
ffmpeg -v error -y -ss 3.0 -t 3.0 -i app-screens/forecast/forecast_he_height.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];[b]crop=840:760:120:500,scale=1080:977:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:520,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/tr_tmrw.mp4
# before / after split (same man): top = hook first frame, bottom = end of the wipe clip
ffmpeg -v error -y -i $G/tr_hook.mp4 -frames:v 1 -vf "crop=1080:952:0:700" /tmp/px/bef.png
curl -sSfL -m 60 -o /tmp/px/clean.webp "https://mcp-tools-z-image-turbo.hf.space/--replicas/lq8v9/gradio_api/file=/tmp/gradio/31407505d87629522687728254fdfbb25988ee08996433d2956ef8d8b8a42df3/image.webp" && ffmpeg -v error -y -i /tmp/px/clean.webp -vf "scale=1080:1920:flags=lanczos,crop=1080:952:0:500" /tmp/px/aft.png || ffmpeg -v error -y -sseof -0.6 -i $G/tr_wipe.mp4 -frames:v 1 -vf "crop=1080:952:0:760" /tmp/px/aft.png
cp /tmp/px/aft.png out/ci/d01/review/aft.png
ffmpeg -v error -y -loop 1 -t 3.0 -i /tmp/px/bef.png -loop 1 -t 3.0 -i /tmp/px/aft.png -filter_complex "color=c=0x2D242A:s=1080x16:d=3[d];[0][d][1]vstack=inputs=3,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/tr_split.mp4
for f in $G/tr_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d01/review/cut_$n.jpg; done
ls -la $G/tr_*
