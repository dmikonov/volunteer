# 09.11 night: 12.11 HE wetsuit drying (С05) + EN last wave (Ф13). Survey real shots.
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
R=out/ci/d09/review; S=out/ci/d09/src; mkdir -p $R $S /tmp/st
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
for id in 1127 1076 1042 1045 1016 1002 1075 21286; do ( for q in 1080 720; do curl -sSfL -A "$UA" -m 280 -o $S/m$id.mp4 https://assets.mixkit.co/videos/$id/$id-$q.mp4 && break; done ) & done
for x in 7938104:uhd_2560_1440_25fps 7938106:uhd_2560_1440_25fps 7938432:uhd_2560_1440_25fps 7938443:uhd_2560_1440_25fps 7938445:uhd_2560_1440_25fps 8713116:hd_1080_1920_25fps 8713109:hd_1080_1920_25fps; do id=${x%:*}; q=${x#*:}; ( curl -sSfL -A "$UA" -m 280 -o $S/p$id.mp4 "https://videos.pexels.com/video-files/$id/$id-$q.mp4" ) & done; wait
for f in $S/*.mp4; do n=$(basename $f .mp4); ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 $f | tr '\n' ' ' > $R/$n.info
 ffmpeg -nostdin -v error -y -i $f -vf "fps=2,scale=-2:150,drawtext=text='$n %{pts\:hms}':x=3:y=3:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=12x3" -frames:v 1 $R/${n}_sheet.jpg & done; wait; ls -la $R; cat $R/*.info
