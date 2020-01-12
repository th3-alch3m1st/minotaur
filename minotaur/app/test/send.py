#!/usr/bin/env python
'''
    This is the publisher

'''
import pika
import sys, logging

# Connect to RabbitMQ on the localhost, if different machine use IP/hostname
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', connection_attempts=5, retry_delay=5, heartbeat=300))
channel = connection.channel()

#'test' exchange to send the message to
channel.exchange_declare(exchange='test', exchange_type='direct', passive=False, durable=True, auto_delete=False)

scan_type = sys.argv[1] if len(sys.argv) >1 else 'info'
message = ' '.join(sys.argv[1:]) or "info"

channel.basic_publish(exchange='test', routing_key=scan_type, body=message)

print(" [x] Sent %r:%r" % (scan_type, message))

channel.close()
