#!/usr/bin/env python
'''
    This is the main subscriber

'''
import pika
import sys,os
from datetime import datetime
from subprocess import Popen, PIPE

def rabbitmqConnection(options, callback):
    while True:
        try:
            # Connect to RabbitMQ using IP/hostname
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', connection_attempts=5, retry_delay=5))

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

        for scan_type in options:
            channel.queue_bind(exchange='test', queue=queue_name, routing_key=scan_type)

        print(" [*] Waiting for logs. To exit press CTRL+C")

        # This specific callback should receive msg from hello queue
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        try:
            # Never ending loop to wait for messages
            channel.start_consuming()
        except pika.exceptions.ConnectionClosed:
            print('Connection closed. Reconnecting to RabbitMQ')
            continue
        except KeyboardInterrupt:
            channel.stop_consuming()

        connection.close()
        break
