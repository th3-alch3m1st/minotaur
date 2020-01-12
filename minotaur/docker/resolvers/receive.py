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
    if method.routing_key == 'brute':
        print("Start resolvers")
        process = Popen(['python3', '/tools/fresh.py/fresh.py', '-o', '/tools/input/resolvers.txt'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print("finished resolvers")

app.spawn_subscriber.rabbitmqConnection(options, callback)
