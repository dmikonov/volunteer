# 04.11 night: first winter storm (HE, 07.11). All real Mixkit footage (free licence): 17877 waves over a promenade in a storm, 48855 storm front with messy brown waves,
# 17877 waves over a promenade, 45239 lighthouse in a storm, 18736 storm clouds, 47948 lightning, 48855 storm front with foam to the horizon, 48525 aerial rows of waves, 22451 rough sea at sunset, 17969 gulls under storm clouds, 36833 aerial surfer on a clean wave, 1075 surfer catching a wave.
[ -f /s17/gen/sm_app.mp4 ] && exit 0
G=/s17/gen; mkdir -p $G /tmp/px out/ci/d04/review out/ci/d04/gen
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 17877 48855 47948 48527 45239 36833 1076; do [ -s /tmp/px/m$id.mp4 ] || for q in 1080 720; do curl -sSfL -A "$UA" -m 300 -o /tmp/px/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done; done
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cut m17877 11.0 3.6 0.55 0.50 sm_hook
cut m45239 4.0 4.5 0.30 0.35 sm_mess
cut m48855 0.0 3.0 0.45 0.50 sm_pier
cut m47948 0.9 1.7 0.55 0.55 sm_bolt
cut m48527 0.5 4.5 0.50 0.50 sm_foam
cut m48527 9.0 4.0 0.50 0.50 sm_sets
cut m45239 14.0 3.8 0.32 0.36 sm_calm
cut m36833 5.1 2.6 0.74 0.80 sm_clean
cut m36833 7.7 3.5 0.80 0.86 sm_save
# hook: take the purple cast off the promenade clip (grey storm look)
ffmpeg -v error -y -i $G/sm_hook.mp4 -vf "hue=s=0.25,eq=contrast=1.08:brightness=-0.03,format=yuv420p" -an -c:v libx264 -crf 15 $G/sm_hook_g.mp4 && mv $G/sm_hook_g.mp4 $G/sm_hook.mp4
cut m1076 8.0 5.0 0.50 0.55 sm_tmrw
# app: weekly forecast bars (days 19-22: 70, 59, 39 red, 39 red, HE forecast recording), 2x crop over the blurred screen: insert 1080x1120 (58% of the frame)
ffmpeg -v error -y -ss 2.0 -t 4.2 -i app-screens/forecast/forecast_he_best.mp4 -filter_complex "[0:v]fps=25,split=2[a][b];[a]crop=1080:1920:0:209,boxblur=28,eq=brightness=-0.28[bg];[b]crop=600:450:365:1150,scale=1080:810:flags=lanczos,unsharp=5:5:0.4[fg];[bg][fg]overlay=0:660,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/sm_app.mp4
for f in $G/sm_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 out/ci/d04/review/cut_$n.jpg; done
ls -la $G/sm_*
