#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os
import time
import app.spawn_subscriber
from subprocess import Popen, PIPE

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))
    if method.routing_key == 'passive':
        print('Start amass')
        process = Popen(['amass', 'enum', '--passive', '-d', opt[1]], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print stdout
        print('finished amass')

app.spawn_subscriber.rabbitmqConnection(options, callback)
