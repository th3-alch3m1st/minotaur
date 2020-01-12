#!/bin/bash

while read -r line; do
    if [ ! -d /tools/output/$line ]; then
        mkdir -p /tools/output/$line
    fi
    /tools/massdns/scripts/subbrute.py /tools/input/alldns.txt ${line} | /bin/massdns -r /tools/input/resolvers.txt -t A -o S -w /tools/output/$line/massdns.$line.$(date +%Y%m%d%H%M%S)
done < /tools/input/domain.txt
