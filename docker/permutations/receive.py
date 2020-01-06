#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os,time
import app.spawn_subscriber
from datetime import datetime
from subprocess import Popen, PIPE

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [permutations]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Check if folder exists
    time.sleep(2)
    filepath = '/tools/output/permutations'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Start scan
    if method.routing_key == 'permutations':
        print("Start dnsgen")
        with open(filepath + '/permutations-' + opt[1] + '.' + opt[2], 'wb') as out:
            permutations_process = Popen(['dnsgen', '-'], stdin=PIPE, stdout=out)
            permutations_process.communicate(opt[1])
        print("finished dnsgen")

        send_process = Popen([ 'python2.7', '/tools/app/send.py', 'resolve', opt[1], opt[2] ])
        send_process.communicate()[0]
        send_process.wait()

    # Start Resolving
    # $TOOLS_DIR/massdns/bin/massdns - -r $TOOLS_DIR/massdns/lists/resolvers.txt -t A -o S -w $TMP_FILE
    # ./scripts/ptr.py | ./bin/massdns -r lists/resolvers.txt -t PTR -w ptr.txt

app.spawn_subscriber.rabbitmqConnection(options, callback)
