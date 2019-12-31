#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os
import time
from subprocess import Popen, PIPE

try:
    # Connect to RabbitMQ on the localhost, if different machine use IP/hostname
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', connection_attempts=5, retry_delay=5))

    # https://www.programcreek.com/python/example/13392/pika.BlockingConnection
    assert connection.is_open is True
    assert connection.is_closed is False
    sys.stdout.write('Connection to RabbitMQ OK')

except Exception as e:
    msg = ('ampq connection failed ({})'.format(str(e)))
    print(msg)

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
    if method.routing_key == 'brute':
        print("Start resolvers")
        process = Popen(['python3', '/tools/fresh.py/fresh.py', '-o', '/tools/input/resolvers.txt'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print("finished resolvers")

try:
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
except pika.exceptions.ConnectionClosed:
    sys.stdout.write('Reconnecting to RabbitMQ')
    connection.channel()
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# Never ending loop to wait for messages
channel.start_consuming()
