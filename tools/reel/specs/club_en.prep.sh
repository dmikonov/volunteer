# 31.10 night: SurfTribe Club for coaches (03.11), HE and EN. Real stock: Pexels 8907784 (group in the water, one woman catches a wave and rides),
# Pexels 6299804 (coach teaching a pop-up on the sand), Pexels 8678056 (feet running on sand, HE teaser). Free Pexels licence.
# AI: cl_night (coach at the laptop at night), Z-Image seed 311031 + Wan 2.2. App: real Club recordings 29.09 (EN 13-52-20, HE 09-22-08).
[ -f /s17/gen/cl_list_he.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d31/review
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 8907784 6299804 8678056; do u=$(grep "^$id " out/ci/d28/review/resolved.txt | cut -d' ' -f2); [ -s /tmp/px/p$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p$id.mp4 "$u" || echo "FAIL $id"; done
[ -s /tmp/px/night.mp4 ] || curl -sSfL -m 120 -o /tmp/px/night.mp4 "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas/nv7ft/gradio_api/file=/tmp/gradio/274c56d18f03d78f3f52995557249cfe235e561a95e429b93bf910b89d1c6858/tmpejrm3adv.mp4" || echo "FAIL night"
cp /tmp/px/night.mp4 out/ci/d31/review/night_raw.mp4 2>/dev/null
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut p8907784 0.0 4.5 0.47 0.47 cl_hook
cut p8907784 15.5 4.0 0.50 0.52 cl_ride
cut p8907784 23.0 4.0 0.53 0.53 cl_tmrw_en
cut p6299804 2.0 4.0 0.60 0.60 cl_coach
cut p6299804 9.0 4.0 0.60 0.60 cl_coach2
cut p8678056 0.5 3.5 0.45 0.45 cl_tmrw_he
ffmpeg -v error -y -i /tmp/px/night.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/cl_night.mp4
# app inserts: real recordings, zoom 1.08 (body text 42 -> 45 px), under a plum band for the title; stills where the screen would scroll or show the keyboard
app(){ f=$1; ss=$2; t=$3; y=$4; n=$5; still=$6
  if [ -n "$still" ]; then ffmpeg -v error -y -ss $ss -i app-screens/ScreenRecording_09-29-2026_$f.mp4 -frames:v 1 /tmp/px/$n.png
    ffmpeg -v error -y -loop 1 -t $t -i /tmp/px/$n.png -vf "crop=1000:1444:40:$y,scale=1080:1560:flags=lanczos,pad=1080:1920:0:350:0x2D242A,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/$n.mp4
  else ffmpeg -v error -y -ss $ss -t $t -i app-screens/ScreenRecording_09-29-2026_$f.mp4 -vf "crop=1000:1444:40:$y,scale=1080:1560:flags=lanczos,pad=1080:1920:0:350:0x2D242A,fps=25,format=yuv420p" -an -c:v libx264 -crf 14 $G/$n.mp4; fi; }
rm -f $G/cl_film_* $G/cl_card_* $G/cl_note_* $G/cl_list_*
app 13-52-20_1 19.6 3.2 330 cl_film_en
app 13-52-20_1 25.3 3.6 540 cl_card_en 1
app 13-52-20_1 28.5 3.0 600 cl_note_en 1
app 13-52-20_1 23.2 2.0 220 cl_list_en 1
app 09-22-08_1 16.5 4.0 330 cl_film_he
app 09-22-08_1 9.6 3.6 440 cl_card_he 1
app 09-22-08_1 9.6 3.0 720 cl_note_he 1
app 09-22-08_1 6.6 2.0 240 cl_list_he 1
for f in $G/cl_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d31/review/cut_$n.jpg; done
ls -la $G/cl_*
