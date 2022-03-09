#!/bin/bash
cd pyTestsApp


# Depending on the machine, the test may take some time,
# take into account the machine specifications when
# setting the number of repetitions.

if [[ $# -ne 1 ]]
then
	echo "Invalid number of arguments"
	echo "Usage: "$0" <number of repetitions>"
	exit
fi

declare -i numRep=$1
declare -i count=0
	
echo "Num rep: "$numRep
(( count+=1 ))
echo "Iteration "$count
python test_all.py 2>&1

error=$?

while (( $error == 0  && $count < $numRep ))
do
	(( count+=1 ))
	echo "Iteration "$count
	python test_all.py 2>&1
	error=$?
done

if (( $error != 0 ))
then
	echo ""
	echo "ERROR OCCURED: Number of iterations: "$count
else
	echo ""
	echo "OK: Number of iterations: "$count
fi
exit $?





