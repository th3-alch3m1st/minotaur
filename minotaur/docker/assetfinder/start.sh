#!/bin/bash

while read -r line; do
    if [ ! -d /tools/output/$line ]; then
        mkdir -p /tools/output/$line
    fi
    /go/bin/assetfinder $line > /tools/output/$line/assetfinder.$line.$(date +%Y%m%d%H%M%S)
done < /tools/input/domain.txt
