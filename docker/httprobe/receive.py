#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os,time
import app.spawn_subscriber
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [permutations] [alive] [resolve]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    # body variable will contain `passive domain.com`
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Check if folder exists
    filepath = '/tools/output/' + opt[1]
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Start scan
    if method.routing_key == 'alive':
        print("Start httprobe")
        input_file = open(filepath + '/subdomains-' + opt[1] + '.' + opt[2], 'rb')
        with open(filepath + "/alive-" + opt[1] + "." + opt[2],"wb") as out:
            httprobe_process = Popen(['/go/bin/httprobe', '-p', 'http:8080', 'https:8443', '-c', '150', '-t', '500'], stdin=input_file, stdout=out, stderr=STDOUT)
            httprobe_process.communicate()[0]
            httprobe_process.wait()
        print("finished httprobe")

app.spawn_subscriber.rabbitmqConnection(options, callback)
