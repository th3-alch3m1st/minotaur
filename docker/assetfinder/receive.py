#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os
import time
from subprocess import Popen, PIPE

print('sleeeeeeeeeeeeeeeeeeeeep assetfinder')
time.sleep(20)

# Connect to RabbitMQ on the localhost, if different machine use IP/hostname
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# 'test' exchange to send the message to
channel.exchange_declare(exchange='test', exchange_type='direct')

# The server will choose a random queue name
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

for move in options:
    channel.queue_bind(exchange='test', queue=queue_name, routing_key=move)

print(" [*] Waiting for logs. To exit press CTRL+C")

def callback(ch, method, properties, body):
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))
    if method.routing_key == 'passive':
        print("Start assetfinder")
        process = Popen(['/go/bin/assetfinder', opt[1]], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print stdout
        print("finished assetfinder")

# This specific callback should receive msg from hello queue
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# Never ending loop to wait for messages
channel.start_consuming()
