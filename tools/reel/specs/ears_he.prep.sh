# 06.11 night: HE 09.11 (swapped from 11.11) "ears in winter: surf earplugs + hood". Generated: Z-Image Turbo 61121/61124/61123/61125/61126 + Wan 2.2 (same man). Real: Pexels 8713107 (cold sea from above), 8713106 (walking into the sea), Mixkit 1032 (running on the beach). App: HE forecast, water temperature tile.
[ -f /s17/gen/er_app.mp4 ] && [ -s /s17/gen/er_ear.mp4 ] && exit 0
G=/s17/gen; R=out/ci/d06e/review; mkdir -p $G /tmp/px $R out/ci/d06e/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
while read n u; do [ -s /tmp/px/$n.mp4 ] || curl -sSfL -m 120 -o /tmp/px/$n.mp4 "$u" || cp out/ci/d06e/gen/$n.mp4 /tmp/px/$n.mp4 || echo "FETCH FAIL $n"; cp -n /tmp/px/$n.mp4 out/ci/d06e/gen/$n.mp4 2>/dev/null; done < tools/reel/ci/d06e_list.txt
for id in 8713107 8713106 8713103; do [ -s /tmp/px/p$id.mp4 ] || curl -sSfL -A "$UA" -m 300 -o /tmp/px/p$id.mp4 https://videos.pexels.com/video-files/$id/$id-hd_1080_1920_25fps.mp4; done
for id in 1032; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
g(){ n=$1; ss=$2; t=$3; o=$4; ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$n.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$o.mp4; }
p(){ id=$1; ss=$2; t=$3; o=$4; ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/p$id.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$o.mp4; }
g e_hook 0 3.5 er_hook
g e_ear 0 3.0 er_ear
g e_plug 0 3.0 er_plug
g e_hood 0 3.0 er_hood
g e_ride 0 3.0 er_ride
g e_towel 0 3.0 er_towel
p 8713107 1.0 5.0 er_cold
p 8713106 2.0 5.0 er_walk
p 8713103 1.0 3.0 er_cold2
ffmpeg -v error -y -ss 2.0 -t 4.0 -i /tmp/px/m1032.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:(iw-1080)/2:0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/er_tmrw.mp4
# app: water temperature tile, whole screen blurred behind, tile x2 in the centre band
ffmpeg -v error -y -i app-screens/forecast/forecast_he_water.mp4 -vf "fps=1,scale=270:-2,tile=8x1" -frames:v 1 $R/app_water_sheet.jpg
ffmpeg -v error -y -ss 4.2 -t 2.3 -i app-screens/forecast/forecast_he_water.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.30[bg];[b]crop=550:366:130:1254,scale=962:640:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=59:640,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/er_app.mp4
for f in $G/er_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=5,scale=180:-2,tile=18x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/er_*
