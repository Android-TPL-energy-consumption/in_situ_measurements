#!/sbin/adbdsh

#It runs a command periodically and writes its output in a file.
#First parameter is the time in seconds between different executions.
#Second parameter is the command to run.
#Third parameter is the file which will contain the output.
#https://raw.githubusercontent.com/rsain/Android-TPLs/master/scripts/runcommand.sh

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
else
	> $3
	while :; do
		eval $2 >> $3;
		sleep $1;
	done
fi
