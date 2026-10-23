# 23.10 rip v3 + Dima's notes: round logo all reel, separate app line with title, brand said as "Surf Tribe"
set -x
O=out/ci/rip3/takes; mkdir -p $O; B=https://dmikonov-f5-hebrew.hf.space/--replicas/jzwpl/gradio_api/file=/tmp/gradio
curl -sSfL --retry 2 -m 120 -o $O/L8_v2_s11.wav $B/3d5fbc683e886b64d1063f9727e5179fdf4939ae8488e04422d1b8aea1db1eba/tmpj5m9esur.wav || echo FAIL1
curl -sSfL --retry 2 -m 120 -o $O/L8_v2_s23.wav $B/814b9fd13d9978c1fc8732a873b7bc50042fcd59fc9516c4230ee77116aff7a2/tmperuy8o6z.wav || echo FAIL2
curl -sSfL --retry 2 -m 120 -o $O/L9_app_s11.wav $B/6e1a2f5630fb9ffe3d7d2309e3eacbdb26d13968861c7fd2274da29a6a2f3629/tmp62kmyhyl.wav || echo FAIL3
curl -sSfL --retry 2 -m 120 -o $O/L9_app_s23.wav $B/70ff14658d847b222f6957d8e9cf716c87f9dc015ec61e10483fe275eb3d7b5b/tmp1i_itidk.wav || echo FAIL4
ls -la $O | tail -5
timeout 2700 bash tools/reel/ci/build_reels.sh
