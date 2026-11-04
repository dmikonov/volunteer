# 22.10 knees v3: bridge clips 704x1280 (assets/knees5), split and app panel
set -e
G=/s17/gen; mkdir -p $G
for c in stiff crouch low; do [ -f assets/knees5/k5_${c}_bridge.mp4 ] && cp assets/knees5/k5_${c}_bridge.mp4 $G/k5_$c.mp4; done
[ -f $G/k5_low.mp4 ] || ffmpeg -v error -y -ss 1.3 -i $G/k5_crouch.mp4 -t 2.6 -c:v libx264 -crf 12 $G/k5_low.mp4   # fallback if the low-ride clip is missing
# split: left = stiff (0-1.3 then hold), right = crouch (1.2-2.6 then hold); same start frame = same surfer and wave
ffmpeg -v error -y -i $G/k5_stiff.mp4 -i $G/k5_crouch.mp4 -filter_complex "\
[0:v]trim=0:1.3,setpts=PTS-STARTPTS,fps=25,scale=-2:1920:flags=lanczos,crop=536:1920:(iw-536)*0.56,tpad=stop_mode=clone:stop_duration=3[l];\
[1:v]trim=1.2:2.6,setpts=PTS-STARTPTS,fps=25,scale=-2:1920:flags=lanczos,crop=536:1920:(iw-536)*0.62,tpad=stop_mode=clone:stop_duration=3[r];\
color=c=0xF5F1F7:s=8x1920:r=25[d];[l][d][r]hstack=3,trim=duration=4.0,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 14 -preset medium $G/k5_split.mp4
# app: GAL ride replay (10-12 recording 55.8-58.8), skeleton with knee angle zoomed 2x, app's own label under it
ffmpeg -v error -y -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -filter_complex "\
[0:v]trim=55.8:58.8,setpts=PTS-STARTPTS,fps=25,split=3[a][b][c];\
[a]crop=1080:1920:0:214,boxblur=30,eq=brightness=-0.3[bg];\
[b]crop=540:560:390:1050,scale=1080:1120:flags=lanczos,unsharp=5:5:0.5[fg];\
[c]crop=960:150:60:1765[lab];[bg][fg]overlay=0:470[t];[t][lab]overlay=60:1600,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium -t 3 $G/kb_app.mp4
cp out/ci/rip/gen/rp_wide.mp4 out/ci/rip/gen/rp_watch.mp4 $G/
