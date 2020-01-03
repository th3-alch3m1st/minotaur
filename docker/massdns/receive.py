#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os
import time
import app.spawn_subscriber
from datetime import datetime
from subprocess import Popen, PIPE

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Grab date and add to filename
    now = datetime.now()
    date = now.strftime("%Y%m%d%H%M%S")

    # Check if folder exists
    filepath = '/tools/output/'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Start scan
    if method.routing_key == 'brute':
        print("Start massdns")
        with open(filepath + 'brute-force-' + opt[1] + '.' + date, 'wb') as out:
            subbrute_process = Popen(['/tools/massdns/scripts/subbrute.py', '/tools/input/alldns.txt', opt[1]], stdout=PIPE)
            massdns_process = Popen(['/bin/massdns', '-r', '/tools/input/resolvers.txt', '-t', 'A', '-o' , 'S'], stdin=subbrute_process.stdout, stdout=out)
            subbrute_process.stdout.close()
            massdns_process.communicate()[0]
        print("finished massdns")

app.spawn_subscriber.rabbitmqConnection(options, callback)

#/tools/massdns/scripts/subbrute.py /tools/input/alldns.txt ${line} | /bin/massdns -r /tools/input/resolvers.txt -t A -o S -w /tools/output/$line/massdns.$line.$(date +%Y%m%d%H%M%S)

