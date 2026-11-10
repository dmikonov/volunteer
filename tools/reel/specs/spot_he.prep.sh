# 11.11 night: 14.11 HE "why instructors pick the boring beach" (Сп01, why-form). Real footage only:
# Pexels 9823083 (Tel Aviv, beginners on soft boards, overcast), Mixkit ROCK (waves on rocks), Pexels 4093785 (Tel Aviv coast from Jaffa),
# Pexels 5902497 (dark patches near shore), st_rip1 from rip3 (rip channel, jetty at the end), Pexels 18224893 (sandy beach aerial), 20256023 (coast aerial).
G=/s17/gen; S=out/ci/d11/src; R=out/ci/d11/review; mkdir -p $G $R /tmp/px
[ -f $G/sp_tmrw.mp4 ] && exit 0
ROCK=${ROCK:-m9294}; RSS=${RSS:-0.0}; RC=${RC:-0.30}
cut(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
# zoomed cut: z = height scale of the 1080p source, cx/cy = centre of the crop (0-1)
cutz(){ src=$1; ss=$2; t=$3; cx=$4; cy=$5; z=$6; n=$7
  ffmpeg -v error -y -ss $ss -t $t -i $S/$src.mp4 -vf "scale=-2:$z:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,$cx*iw-540))':'max(0,min(ih-1920,$cy*ih-960))',fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
cutz p9823083 0.0 4.2 0.66 0.73 3200 sp_hook
cut $ROCK $RSS 4.0 $RC $RC sp_rocks
cut p4093785 1.0 4.4 0.30 0.36 sp_look
cut p5902497 4.0 4.6 0.20 0.22 sp_dark
cutz p9823083 11.0 3.6 0.33 0.77 3000 sp_fall
cut p18224893 0.0 3.4 0.42 0.46 sp_send
cut p20256023 1.5 4.0 0.50 0.54 sp_tmrw
# app: "שאלו את המאמן" button (HE recording 28.09 15:24 at 11.6 s) big over the sandy beach aerial
ffmpeg -v error -y -ss 11.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/px/he_coach.png
cut p20256023 8.0 4.0 0.50 0.52 sp_appbg
ffmpeg -v error -y -i $G/sp_appbg.mp4 -loop 1 -i /tmp/px/he_coach.png -filter_complex "[1:v]crop=980:220:50:1440,scale=1080:242:flags=lanczos[fg];[0:v][fg]overlay=0:1060:shortest=1,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/sp_app.mp4
rm -f $G/sp_appbg.mp4
for f in $G/sp_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/sp_*
