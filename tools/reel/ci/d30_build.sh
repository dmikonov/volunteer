# 30.10 film a friend HE (+ fetch Wan clips for film and chest_en)
set -x
sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg >/dev/null
sudo mkdir -p /s17/gen && sudo chown -R $USER /s17
O=out/ci/d30/gen; mkdir -p $O
B=https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space/--replicas
while read n u; do [ -s $O/$n.mp4 ] || curl -sSfL -m 120 -o $O/$n.mp4 "$B/$u" || echo "FAIL $n"; done <<'L'
fm_film2_raw kbr8z/gradio_api/file=/tmp/gradio/e2fdc56939a2750e497f6e02dd2008c5f28b23f84acac19bbec7e6bf7332800b/tmp_iw6q8hr.mp4
fm_board_raw kbr8z/gradio_api/file=/tmp/gradio/7514c6f60ac8768331473cb6db656be154008f45215a633e3270b13cdcca5c3e/tmpn2rnegc7.mp4
ch_err_raw bwlzl/gradio_api/file=/tmp/gradio/b9c74ae87b540c2d19bce09affa4d16f94883cf1c4846d9a8abee554751d6718/tmppgx8_xcy.mp4
ch_err16_raw bwlzl/gradio_api/file=/tmp/gradio/fffbf7553c65015b6df5913baf8aa83d5e22c39ec6543cc6ec396aaaeb81cd10/tmpl_6p6ui1.mp4
L
for n in fm_board_raw ch_err_raw ch_err16_raw; do ffmpeg -nostdin -v error -y -i $O/$n.mp4 -vf "fps=5,scale=-2:300,tile=9x2" -frames:v 1 $O/${n}_sheet.jpg; done
mkdir -p out/ci/d30; bash -x tools/reel/specs/film_he.prep.sh > out/ci/d30/prep_film.log 2>&1; ls -la /s17/gen >> out/ci/d30/prep_film.log
timeout 2700 bash tools/reel/ci/build_reels.sh
