#!/bin/bash

# Exit immediately if a command exits with a non-zero status. E: error trace
#set -eE -o functrace

/opt/snap/bin/snap --nosplash --nogui --modules --update-all 2>&1 | while read -r line; do
    echo "$line"
    [ "$line" = "updates=0" ] && sleep 2 && pkill -TERM -f "snap/jre/bin/java"
done

exit 0

