#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika

# Connect to RabbitMQ on the localhost, if different machine use IP/hostname
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost')))
channel = connection.channel()

# 'hello' queue to send the message to
channel.queue_declare(queue='hello')

# To receive a msg you need to subscribe a callback to a queue
# When a msg is received this callback is called
def callback(ch, method, properties, body):
    print(" [x] Receiver %r" % body)

# This specific callback should receive msg from hello queue
channel.basic_consume(queue='hello', auto_ack=True, on_message_callback=callback)

# Never ending loop to wait for messages
print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming
