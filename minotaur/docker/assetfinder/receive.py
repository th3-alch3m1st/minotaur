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
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    # body variable will contain `passive domain.com`
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Grab date and add to filename
    now = datetime.now()
    date = now.strftime("%Y%m%d%H%M%S")

    # Check if folder exists
    filepath = '/tools/output/' + opt[1]
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Send domain for brute force
    print('Send domain for brute force')
    send_process = Popen(['python', '/tools/app/send.py', 'brute', opt[1], date])
    send_process.communicate()[0]

    # Start scan
    if method.routing_key == 'passive':
        print("Start assetfinder")
        with open(filepath + "/assetfinder-" + opt[1] + "." + date,"wb") as out:
            assetfinder_process = Popen(['/go/bin/assetfinder', opt[1]], stdout=out, stderr=STDOUT)
            #assetfinder_process.communicate()[0]
            assetfinder_process.wait()
            out.flush()
            os.fsync(out)
            out.close()
        print("finished assetfinder")

app.spawn_subscriber.rabbitmqConnection(options, callback)
