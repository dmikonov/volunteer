# rebuild video only (keeps voice). usage: bash run2.sh <workdir>
W=$1; cd /s17/rp
rm -rf $W/seg
python3 build.py $W > $W/build.log 2>&1 && python3 ov.py $W > $W/ov.log 2>&1 && python3 post.py $W > $W/post.log 2>&1
echo "EXIT $?" >> $W/run.log
