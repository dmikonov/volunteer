# 12.11 night r2: Bondi aerials (Macourt Media, one location) for 15.11 rip channel
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d12/review; S=out/ci/d12/src; mkdir -p $R $S
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for p in "31845107/13566757_2560_1440_30fps" "31845098/13566763_2560_1440_30fps" "32889391/14016951_2560_1440_30fps" "32889390/14016963_2560_1440_30fps"; do id=${p%%/*}
  ( curl -sSfL -A "$UA" -m 280 -o /tmp/p$id.mp4 "https://videos.pexels.com/video-files/$p.mp4" && ffmpeg -nostdin -v error -y -i /tmp/p$id.mp4 -vf "scale=1920:-2" -c:v libx264 -crf 17 -preset fast -an $S/p$id.mp4 ) & done; wait
for id in 31845107 31845098 32889391 32889390; do f=$S/p$id.mp4; n=p$id; ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/$n.info
 ffmpeg -nostdin -v error -y -i $f -vf "fps=2,scale=-2:200,drawtext=text='$n %{pts\:hms}':x=3:y=3:fontsize=15:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=10x4" -frames:v 1 $R/${n}_sheet.jpg & done; wait
find $S -size +80M -delete; ls -la $S $R; cat $R/*.info
