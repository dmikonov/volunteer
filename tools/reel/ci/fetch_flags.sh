# 21.10 fork C: clips for flags_he (24.10). Full URLs in fetch_flags_list.txt; rain still -> slow push-in mp4; app recording sheet.
set -x
O=out/ci/flags/gen; mkdir -p $O
sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true
while read n u; do curl -sSfLo $O/$n.mp4 "$u"; done < tools/reel/ci/fetch_flags_list.txt
curl -sSfLo /tmp/rain.webp "https://mcp-tools-z-image-turbo.hf.space/--replicas/7sjf9/gradio_api/file=/tmp/gradio/2bde56a0fb46b662a82cda588ea9403e9d2ee64944099cf420e0741ac9fa05b8/image.webp"
ffmpeg -nostdin -v error -y -loop 1 -i /tmp/rain.webp -vf "scale=1440:2560,zoompan=z='1+0.0016*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=100:s=720x1280:fps=25" -frames:v 100 -c:v libx264 -crf 16 -pix_fmt yuv420p $O/fl_rain.mp4
for f in $O/fl_*.mp4; do n=$(basename $f .mp4); ffmpeg -nostdin -v error -y -i $f -vf "fps=5,scale=200:-1,tile=6x3" -frames:v 1 $O/${n}_sheet.jpg; done
A=app-screens/ScreenRecording_09-28-2026_10-56-35_1_4.mp4
ffmpeg -nostdin -v error -y -ss 8 -t 10 -i $A -vf "fps=2,scale=240:-1,drawtext=text='%{pts\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow,tile=5x4" -frames:v 1 $O/app14_sheet.jpg
ffprobe -v error -show_entries stream=width,height -of csv=p=0 $A > $O/app14_size.txt
