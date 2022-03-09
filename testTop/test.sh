#!/bin/bash
cd pyTestsApp
#nosetests -v -x --debug-log=testlog.stderr --exclude='Timestamping'
err1=0
err2=0
python test_all.py 2>&1
if [[ $? != 0 ]]
then 
    err1=$((err1 + 1))
    #echo "err1:" $err1
   
fi
python test_all.py -i 2>&1
if [[ $? != 0 ]]
then 
    err2=$((err2 + 1))
    #echo "err2:" $err2
   
fi
err=$((err1 + err2))
echo ""
echo "Test Global Error" $err
echo "Test 1:" $err1
echo "Test 2 (INIT=YES):" $err2


if [ $err != 0 ]
    then
    #echo "FAILED"
    >&2 echo "UNITTESTS FAILURE"
    exit $err 
fi
