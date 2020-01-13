# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import threading
import time
import pika
import sys,os
from subprocess import Popen, PIPE, STDOUT
import app.send

#LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
#LOGGER = logging.getLogger(__name__)

#logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


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
    #LOGGER.info('Thread id: %s Delivery tag: %s Message body: %s', thread_id, delivery_tag, body)

    opt = body.split(" ")
    domain = opt[1]
    date = opt[2]

    if opt[0] == 'permutations':

        filepath = '/tools/output/permutations'
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        contents = []
        path = '/tools/output/brute-force/'
        files = os.listdir(path)
	for f in files:
            with open(path + f, 'rb') as results:
                contents.extend(results.read().split('\n'))

        # Remove empty strings in list
        contents = filter(None, contents)

        # format is `subdomain.com type x.x.x.x` or `subdomain.com CNAME anotherdomain.com` - split to just keep subdomain.com
        sep = ' '
        subs_list = []
        for item in contents:
            subs_list.append((item.split(sep, 1)[0]).rstrip('.'))

        # Unique subdomains found
        sorted_subdomains = sorted(set(subs_list))

        for subdomain in sorted_subdomains:
            with open(filepath + "/permutations-" + subdomain + "." + date, "wb") as out:
                permutations_process = Popen(['dnsgen', '-'], stdin=PIPE, stdout=out)
                permutations_process.communicate(domain)
                out.flush()
                os.fsync(out)

    cb = functools.partial(ack_message, ch, delivery_tag)
    conn.add_callback_threadsafe(cb)

    for subdomain in sorted_subdomains:
        option = 'resolve'
        message = option + ' ' + subdomain + ' ' + date
        app.send.publish(option, message)

def on_message(ch, method_frame, _header_frame, body, args):
    (conn, thrds) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(conn, ch, delivery_tag, body))
    t.start()
    thrds.append(t)


def rabbitmqConnection(options):
    while True:
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
                'rabbitmq', connection_attempts=5, retry_delay=5, heartbeat=100)
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.exchange_declare(
            exchange='test',
            exchange_type='direct',
            passive=False,
            durable=True,
            auto_delete=False)

        scan_type = options[0]
        channel.queue_declare(queue=scan_type, exclusive=False)
        channel.queue_bind(exchange='test', queue=scan_type, routing_key=scan_type)
        channel.basic_qos(prefetch_count=1)

        threads = []
        on_message_callback = functools.partial(on_message, args=(connection, threads))
        channel.basic_consume(scan_type, on_message_callback)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
            break
        except:
            # Wait for all to complete
            for thread in threads:
                thread.join()
            connection.close()
            continue


options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

rabbitmqConnection(options)
