# foam6 (23.10): real Sept clips (assets/foam6, rotated+graded) + Mixkit 1163 (real) for waist-deep and paddling, app4 insert
set -e
G=/s17/gen; mkdir -p $G
cp assets/foam6/r_*.mp4 $G/
M=assets/stock/mx_1163_1080.mp4; [ -f $M ] || M=assets/stock/mx_1163.mp4
ffmpeg -v error -y -ss 21.2 -t 2.4 -i $M -vf "crop=ih*9/16:ih:iw*0.5:0,eq=brightness=0.05:contrast=1.08,scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 $G/st_waist.mp4
ffmpeg -v error -y -t 3.0 -i assets/gentest/ltx_lie_s21.mp4 -vf "scale=1080:1920:flags=lanczos,fps=25,format=yuv420p" -an -c:v libx264 -crf 16 $G/st_paddle.mp4  # AI (LTX-2.5), clean all 3 s
bash tools/reel/specs/foam5_he.prep.sh
