# Composio sandbox setup (19.10: HF sandbox returns 402). usage: bash setup_cz.sh <sha> <name...>
# /s17 is replaced by $HOME/s17 in every script and spec. Gen clips go to $HOME/s17/gen by hand.
REF=$1; shift; S=$HOME/s17; G=https://raw.githubusercontent.com/dmikonov/volunteer/$REF
mkdir -p $S/gen $S/app $S/rp $S/tip1
curl -sSf -o $S/Rubik.ttf $G/appkit/Rubik.ttf
cd $S/rp && for f in voice.py build.py ov_ff.py post_cz.py audio_fx.py loudfix.py; do curl -sSf -o $f $G/tools/reel/$f; sed -i "s#/s17/#$S/#g; s#'/s17'#'$S'#g" $f; done
for k in "$@"; do mkdir -p $k; curl -sSf -o $k/spec.json $G/tools/reel/specs/$k.json; sed -i "s#/s17/#$S/#g" $k/spec.json; done
echo SETUPDONE
