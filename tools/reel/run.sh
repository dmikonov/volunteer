# usage: bash run.sh <workdir>
W=$1; cd /s17/rp
python3 voice.py $W > $W/voice.log 2>&1 && python3 build.py $W > $W/build.log 2>&1 && flock /tmp/ov.lock python3 ov.py $W > $W/ov.log 2>&1 && python3 post.py $W > $W/post.log 2>&1
echo "EXIT $?" >> $W/run.log
