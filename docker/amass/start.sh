#!/bin/bash

while read -r line; do
	if [ ! -d /tools/output/$line ]; then
        mkdir -p /tools/output/$line
    fi
	amass enum --passive -d $line -o /tools/output/$line/amass.$line.$(date +%Y%m%d%H%M%S)
done < /tools/input/domain.txt
