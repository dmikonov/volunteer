# 30.10 night: stock survey for 02.11 (EN chest up paddling: Pexels Kampus 81545xx one surfer; HE morning glassy vs windy chop)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d30s/review; mkdir -p $R /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
while read n u; do [ -z "$n" ] && continue
 ( curl -sSfL -A "$UA" -m 300 -o /tmp/st/$n.mp4 "$u" || { echo "$n FAIL" >> $R/fail.txt; exit 0; }
   ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate:format=duration -of csv=p=0 /tmp/st/$n.mp4 | tr '\n' ' ' > $R/${n}_info.txt
   ffmpeg -nostdin -v error -y -i /tmp/st/$n.mp4 -vf "fps=2,scale=-2:240,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=8x8" -frames:v 1 $R/${n}_sheet.jpg ) &
done <<'L'
k8155537 https://videos.pexels.com/video-files/8155537/8155537-uhd_2560_1440_25fps.mp4
k8155541 https://videos.pexels.com/video-files/8155541/8155541-uhd_2560_1440_25fps.mp4
k8155551 https://videos.pexels.com/video-files/8155551/8155551-uhd_2560_1440_25fps.mp4
k8154483 https://videos.pexels.com/video-files/8154483/8154483-uhd_2560_1440_25fps.mp4
k8154896 https://videos.pexels.com/video-files/8154896/8154896-uhd_2560_1440_25fps.mp4
k8154903 https://videos.pexels.com/video-files/8154903/8154903-uhd_2560_1440_25fps.mp4
k8154486 https://videos.pexels.com/video-files/8154486/8154486-uhd_2560_1440_25fps.mp4
k8155548 https://videos.pexels.com/video-files/8155548/8155548-uhd_2560_1440_25fps.mp4
k7425557 https://videos.pexels.com/video-files/7425557/7425557-uhd_1440_2560_30fps.mp4
x236273 https://cdn.pixabay.com/video/2024/10/14/236273_large.mp4
g11888526 https://videos.pexels.com/video-files/11888526/11888526-hd_1080_1920_30fps.mp4
g4961454 https://videos.pexels.com/video-files/4961454/4961454-uhd_2560_1440_30fps.mp4
g2873606 https://videos.pexels.com/video-files/2873606/2873606-uhd_2560_1440_25fps.mp4
g159002 https://cdn.pixabay.com/video/2023/04/15/159002-818026264_large.mp4
w18478665 https://videos.pexels.com/video-files/18478665/18478665-uhd_1440_2560_60fps.mp4
w5491966 https://videos.pexels.com/video-files/5491966/5491966-hd_1920_1080_25fps.mp4
w15547520 https://videos.pexels.com/video-files/15547520/15547520-uhd_2560_1440_60fps.mp4
w19345579 https://videos.pexels.com/video-files/19345579/19345579-hd_1920_1080_60fps.mp4
w5404693 https://videos.pexels.com/video-files/5404693/5404693-hd_1920_1080_24fps.mp4
L
wait; ls $R
