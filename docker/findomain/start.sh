#!/bin/bash

while read -r line; do
    if [ ! -d /tools/output/$line ]; then
        mkdir -p /tools/output/$line
    fi
    /tools/findomain-linux -t $line -o
    mv $line.txt /tools/output/$line/findomain.$line.$(date +%Y%m%d%H%M%S)
done < /tools/input/domain.txt

