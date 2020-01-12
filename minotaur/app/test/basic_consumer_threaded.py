# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import threading
import time
import pika
import sys
from subprocess import Popen, PIPE

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def ack_message(ch, delivery_tag):
    """Note that `ch` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if ch.is_open:
        ch.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass


def do_work(conn, ch, delivery_tag, body):
    thread_id = threading.current_thread().ident
    LOGGER.info('Thread id: %s Delivery tag: %s Message body: %s', thread_id,
                delivery_tag, body)

    opt = body.split(" ")
    if opt[0] == 'passive':
        process = Popen(['cat', '/etc/passwd'], stdout=PIPE)
        output, err = process.communicate()
        print output
        ch.basic_publish(exchange='test', routing_key='brute', body='brute test')
    elif opt[0] == 'brute':
        process = Popen(['cat', '/etc/hosts'], stdout=PIPE)
        output, err = process.communicate()
        print output

    cb = functools.partial(ack_message, ch, delivery_tag)
    conn.add_callback_threadsafe(cb)


def on_message(ch, method_frame, _header_frame, body, args):
    (conn, thrds) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(conn, ch, delivery_tag, body))
    t.start()
    thrds.append(t)


options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(
        'rabbitmq', connection_attempts=5, retry_delay=5, heartbeat=100)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.exchange_declare(
    exchange="test",
    exchange_type="direct",
    passive=False,
    durable=True,
    auto_delete=False)
result = channel.queue_declare(queue="stdi", auto_delete=True)
#queue_name = result.method.queue

for scan_type in options:
    channel.queue_bind(
            exchange="test", queue="stdi", routing_key=scan_type)
channel.basic_qos(prefetch_count=1)

threads = []
on_message_callback = functools.partial(on_message, args=(connection, threads))
channel.basic_consume("stdi", on_message_callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()

# Wait for all to complete
for thread in threads:
    thread.join()

connection.close()
