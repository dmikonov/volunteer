# 07.11 night: HE 10.11 "warm-up 5 min" (Ф01). One man through the whole reel: Coverr Madeira scene (free commercial licence, no attribution):
# warm-up 3024 (arm swings on the promenade, back view), steps 6359 (goes down to the sea with the board), looking 6303 (shoulder, profile), washing 9836 (after the session, wet hair).
# app: HE recording 28.09 15:24 at 11.6 s: "body mechanics: shoulder rotation" tile + "שאלו את המאמן" button, big over the blurred screen.
[ -f /s17/gen/wm_app.mp4 ] && exit 0
G=/s17/gen; R=out/ci/d07/review; mkdir -p $G /tmp/px $R
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
dl(){ n=$1; u=$2; [ -s /tmp/px/$n.mp4 ] || cp out/ci/d07/src/$n.mp4 /tmp/px/$n.mp4 2>/dev/null || curl -sSfL -A "$UA" -m 300 -o /tmp/px/$n.mp4 "$u" || echo "FETCH FAIL $n"; }
dl doing-a-warm-up-before-s https://cdn.coverr.co/videos/coverr-doing-a-warm-up-before-surfing-3024/1080p.mp4
dl man-carrying-a-surfboard https://cdn.coverr.co/videos/coverr-man-carrying-a-surfboard-down-the-steps-6359/1080p.mp4
dl man-looking-at-the-sea-n https://cdn.coverr.co/videos/coverr-man-looking-at-the-sea-6303/1080p.mp4
dl man-washing-his-surfboar https://cdn.coverr.co/videos/coverr-man-washing-his-surfboard-9836/1080p.mp4
# full: scale to 1920 high, crop 1080 wide centred on x fraction (pan c0->c1)
full(){ src=$1; ss=$2; t=$3; c0=$4; c1=$5; n=$6
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -vf "scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,($c0+($c1-$c0)*t/$t)*iw-540))':0,fps=25,format=yuv420p" -an -c:v libx264 -crf 15 $G/$n.mp4; }
# wide: arms stay in frame: fg 1200 high (centre x c) over the same clip blurred
wide(){ src=$1; ss=$2; t=$3; c=$4; n=$5
  ffmpeg -v error -y -ss $ss -t $t -i /tmp/px/$src.mp4 -filter_complex "[0:v]split=2[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=30,eq=brightness=-0.12[bg];[b]scale=-2:1200:flags=lanczos,crop=1080:1200:'max(0,min(iw-1080,$c*iw-540))':0[fg];[bg][fg]overlay=0:380,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 15 $G/$n.mp4; }
W=doing-a-warm-up-before-s
full man-carrying-a-surfboard 0.0 3.2 0.75 0.70 wm_hook
full man-looking-at-the-sea-n 2.6 4.0 0.70 0.70 wm_shoulder
wide $W 0.0 3.6 0.46 wm_bridge
wide $W 1.6 3.6 0.47 wm_up
wide $W 5.6 3.0 0.47 wm_head
wide $W 7.8 3.8 0.47 wm_swing
full man-washing-his-surfboar 8.0 4.0 0.50 0.48 wm_after
full man-carrying-a-surfboard 6.0 4.6 0.50 0.40 wm_save
full man-looking-at-the-sea-n 11.0 3.8 0.60 0.57 wm_tmrw
# app insert 1080x855 (45% of the frame), text in it about 45 px
ffmpeg -v error -y -ss 11.6 -i app-screens/ScreenRecording_09-28-2026_15-24-29_1.mp4 -frames:v 1 /tmp/px/he_coach.png
ffmpeg -v error -y -loop 1 -t 4.0 -i /tmp/px/he_coach.png -filter_complex "[0:v]split=2[a][b];[a]crop=1080:1920:0:214,boxblur=28,eq=brightness=-0.3[bg];[b]crop=960:760:60:880,scale=1080:855:flags=lanczos,unsharp=5:5:0.5[fg];[bg][fg]overlay=0:560,fps=25,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 $G/wm_app.mp4
for f in $G/wm_*.mp4; do n=$(basename $f .mp4); ffmpeg -v error -y -i $f -vf "fps=4,scale=180:-2,tile=16x1" -frames:v 1 $R/cut_$n.jpg; done
ls -la $G/wm_*
