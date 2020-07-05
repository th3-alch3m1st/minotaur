# -*- coding: utf-8 -*-
import pika

def connectionPack():
    credentials = pika.PlainCredentials('changeme', 'changeme')
    parameters = pika.ConnectionParameters(
            'rabbitmq', credentials=credentials, connection_attempts=5, retry_delay=5, heartbeat=100)
    connection = pika.BlockingConnection(parameters)

    return connection
