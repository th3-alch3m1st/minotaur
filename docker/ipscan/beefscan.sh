#!/bin/bash

masscan -p 1-65535 $1 --rate 6000 -oG $2/masscan_output.$3.txt 2>/dev/null

#echo "$(cat $2/masscan_output.$3.txt | grep 'Timestamp' | awk '{print $4}' | sort -u)" > hosts.txt

open_ports=$(cat $2/masscan_output.$3.txt | grep 'Timestamp' | awk '{print $7}' | cut -d '/' -f1 | sort -u | paste -sd,)

nmap -sSV -T4 -A -p $open_ports --open -o $2/nmap_result.$3.txt --stylesheet nmap-bootstrap.xsl -oA $2/nmap_result_bootstrap.$3 $1 2>/dev/null

cat $2/masscan_output.$3.txt | grep 'http' | awk '{print $4":"$7}' | awk -F'//' '{print$2"://"$1}' | sed 's/http-alt/http/g' | sed 's/\/open.*$//' | tee $2/dirsearch_result.$3.txt
