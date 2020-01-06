#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import glob
import sys,os,time
import app.spawn_subscriber
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms] [dedup]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    # body variable will contain `dedup domain.com`
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Grab date and add to filename
    now = datetime.now()
    date = now.strftime("%Y%m%d%H%M")

    # Check if folder exists
    filepath = '/tools/output/' + opt[1]
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Start scan
    # It will be easier if I do a scan of a specific domain once a day and then put the results in a folder based on the date of the scan
    # then I will just grab all the files in there
    if method.routing_key == 'dedup':
        print("Start de-dup")

        # File format is tools/output/amass-domain.com.date
        tools = ['amass', 'assetfinder', 'subfinder', 'findomain']
        subdomains = []
        all_subdomains = []
        for tool in tools:
            with open(filepath + '/' + tool + '-' + opt[1] + '.' + opt[2], 'rb') as results:
                subdomains = results.read().split()
            results.close()
            all_subdomains.extend(subdomains)

        sorted_subdomains = sorted(set(all_subdomains))
        with open(filepath + '/subdomains-' + opt[1] + '.' + opt[2], 'wb') as subdomains_file:
            for item in sorted_subdomains:
                subdomains_file.write("%s\n" % item)
        print("finished de-dup")

        for subdomain in sorted_subdomains:
            send_process = Popen(['python', '/tools/app/send.py', 'brute', subdomain, opt[2]])
            send_process.communicate()[0]
            send_process.wait()
            #os.stat('filename').st_size
        print('Send results to massdns for brute force')

app.spawn_subscriber.rabbitmqConnection(options, callback)
