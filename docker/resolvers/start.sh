#!/bin/bash

#while read -r line; do
#    if [ ! -d /tools/output/$line ]; then
#        mkdir -p /tools/output/$line
#    fi
#    echo "$line" | dnsgen - > /tools/output/$line/dnsgen.$line.$(date +%Y%m%d%H%M%S)
#done < /tools/input/domain.txt

python3 /tools/fresh.py/fresh.py -o /tools/input/resolvers.txt
