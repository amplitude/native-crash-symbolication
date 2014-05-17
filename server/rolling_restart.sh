#!/bin/bash

PROGRAM=dash # Name from supervisor.conf
# Time in seconds.
TIME_BETWEEN_RUNNING_CHECKS=1
TIME_BETWEEN_RESTARTS=2

for f in `supervisorctl status | grep -e "^$PROGRAM:" | awk '{print $1}'`; do
  supervisorctl restart $f

  while [ 1 ]; do
    sleep $TIME_BETWEEN_RUNNING_CHECKS
    status=`supervisorctl status $f | awk '{print $2}'`
    if [ "$status" == "RUNNING" ] ; then
      echo $f restarted
      break
    elif [ "$status" == "FATAL" ] ; then
      echo "Error during restart of $f ($status). Stopping rolling update."
      exit 1
    else
      echo "Now: $status"
    fi
  done

  sleep $TIME_BETWEEN_RESTARTS
done
