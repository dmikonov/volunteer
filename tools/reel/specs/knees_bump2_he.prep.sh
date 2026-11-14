# 22.10 knees "small bump" v2 (new script, Dima): same clips as knees_bump + rip teaser clip
set -e
G=/s17/gen; mkdir -p $G
for c in A3 B2 end; do cp assets/knees4/kb_$c.mp4 $G/kb_$c.mp4; done
# trimmed copies: the builder holds the last frame when the voice line is longer than the source
ffmpeg -v error -y -i assets/knees4/kb_A1.mp4 -t 0.85 -c:v libx264 -crf 12 $G/kb_A1h.mp4   # rise with straight legs, board kicks, thrown
ffmpeg -v error -y -i assets/knees4/kb_A1.mp4 -t 0.72 -c:v libx264 -crf 12 $G/kb_A1r.mp4   # replay, stops on the locked-knees frame
ffmpeg -v error -y -ss 0.9 -i assets/knees4/kb_A3.mp4 -t 1.5 -c:v libx264 -crf 12 $G/kb_A3c.mp4   # rides up, legs straighten
ffmpeg -v error -y -ss 0.45 -i assets/knees4/kb_A1.mp4 -t 0.4 -c:v libx264 -crf 12 $G/kb_A1k.mp4  # board kicks, thrown
ffmpeg -v error -y -ss 0.5 -i assets/knees4/kb_B4.mp4 -t 0.95 -c:v libx264 -crf 12 $G/kb_B4t.mp4  # sinks low
ffmpeg -v error -y -i assets/knees4/kb_B2.mp4 -t 0.62 -c:v libx264 -crf 12 $G/kb_B2t.mp4   # low stance, before the board turns
ffmpeg -v error -y -ss 0.55 -i assets/knees4/kb_B1.mp4 -t 0.75 -c:v libx264 -crf 12 $G/kb_B1s.mp4  # steady low stance
# split: left = stiff (A1 0-0.85 then hold), right = soft knees (B1 0-1.7 then hold), same start frame = same bump
ffmpeg -v error -y -i assets/knees4/kb_A1.mp4 -i assets/knees4/kb_B1.mp4 -filter_complex "\
[0:v]trim=0:0.85,setpts=PTS-STARTPTS,fps=25,scale=-2:1920:flags=lanczos,crop=536:1920:(iw-536)*0.62,tpad=stop_mode=clone:stop_duration=3[l];\
[1:v]trim=0:1.70,setpts=PTS-STARTPTS,fps=25,scale=-2:1920:flags=lanczos,crop=536:1920:(iw-536)*0.72,tpad=stop_mode=clone:stop_duration=3[r];\
color=c=0xF5F1F7:s=8x1920:r=25[d];[l][d][r]hstack=3,trim=duration=3.6,unsharp=5:5:0.6,format=yuv420p[v]" -map "[v]" -c:v libx264 -crf 14 -preset medium $G/kb_split.mp4
# app: GAL ride replay (10-12 recording 55.8-58.8): skeleton with knee angle 175/173 zoomed 2x, the app's own label "Straight legs - compress into the knees" under it
ffmpeg -v error -y -i app-screens/ScreenRecording_10-12-2026_13-42-15_1.mp4 -filter_complex "\
[0:v]trim=55.8:58.8,setpts=PTS-STARTPTS,fps=25,split=3[a][b][c];\
[a]crop=1080:1920:0:214,boxblur=30,eq=brightness=-0.3[bg];\
[b]crop=540:560:390:1050,scale=1080:1120:flags=lanczos,unsharp=5:5:0.5[fg];\
[c]crop=960:150:60:1765[lab];[bg][fg]overlay=0:470[t];[t][lab]overlay=60:1600,format=yuv420p[v]" -map "[v]" -an -c:v libx264 -crf 14 -preset medium -t 3 $G/kb_app.mp4
cp out/ci/rip/gen/rp_wide.mp4 out/ci/rip/gen/rp_watch.mp4 $G/
# Hebrew voice: Chatterbox Multilingual takes (voice 3 timbre with intonation, Dima 22.10) -> f5_takes in the spec
python3 -m pip install -q uv
uv run --python 3.11 --index-strategy unsafe-best-match --extra-index-url https://download.pytorch.org/whl/cpu --with "chatterbox-tts>=0.1.4" python tools/reel/cb_takes.py tools/reel/specs/knees_bump2_he.json knees_bump2_he 3
python3 tools/reel/cb_split.py tools/reel/specs/knees_bump2_he.json knees_bump2_he
