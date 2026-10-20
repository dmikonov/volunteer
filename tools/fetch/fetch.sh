#!/bin/bash
# lines: dest_path url   (dest under assets/). Makes a 4 fps contact sheet next to each mp4.
set -e
while read -r dest url; do
  [ -z "$dest" ] && continue; [[ "$dest" == \#* ]] && continue
  [ -f "assets/$dest" ] && continue
  mkdir -p "assets/$(dirname "$dest")"
  curl -sSL --retry 3 -o "assets/$dest" "$url" || { echo "FAIL $dest"; rm -f "assets/$dest"; continue; }
  if [[ "$dest" == *.mp4 ]]; then
    ffmpeg -v error -y -i "assets/$dest" -vf "fps=4,scale=240:-2,tile=7x2" -frames:v 1 "assets/${dest%.mp4}_sheet.jpg" || true
  fi
  echo "OK $dest $(stat -c%s "assets/$dest")"
done < tools/fetch/list.txt
