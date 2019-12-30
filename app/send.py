#!/usr/bin/env python
'''
    This is the publisher

'''
import pika
import sys

# Connect to RabbitMQ on the localhost, if different machine use IP/hostname
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

#'test' exchange to send the message to
channel.exchange_declare(exchange='test', exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) >1 else 'info'
message = ' '.join(sys.argv[1:]) or "info"

channel.basic_publish(exchange='test', routing_key=severity, body=message)

print(" [x] Sent %r:%r" % (severity, message))

connection.close()
