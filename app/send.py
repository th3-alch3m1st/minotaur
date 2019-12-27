#!/usr/bin/env python
'''
    This is the publisher

'''
import pika

# Connect to RabbitMQ on the localhost, if different machine use IP/hostname
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#'hello' queue to send the message to
channel.queue_declare(queue='hello')

# specify exchange to receive message, the default one is identified by an empty string
# routing_key is the queue to which this message should go to
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print("[ x] Sent 'Hello World!'")

connection.close()
