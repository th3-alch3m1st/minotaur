# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import threading
import time
import pika
import sys,os
from netaddr import IPNetwork
from subprocess import Popen, PIPE, STDOUT
import app.send
import app.connection

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

    opt = body.decode().split(" ")
    # message is ip-scan 8.8.8.8/24 google.com 010120201111
    # ip can be either 8.8.8.8 or 8.8.8.8/x
    if len(opt) > 2:
        ip = str(opt[1])
        domain = opt[2]
        date = opt[3]

    if opt[0] == 'ip-scan':

        if ip.find('/') == -1:
            filepath = '/tools/output/' + domain + '/ipscan/' + ip
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            with open('out.txt', 'wb') as out:
                beefscan_process = Popen(['/tools/beefscan.sh', ip, filepath, date], stdout=out, stderr=STDOUT)
                beefscan_process.communicate()[0]
                beefscan_process.wait()

            cb = functools.partial(ack_message, ch, delivery_tag)
            conn.add_callback_threadsafe(cb)

            alive = open(filepath + '/dirsearch_result.' + date + '.txt', 'rb')
            for endpoint in alive:
                option = 'dir-scan'
                message = option + ' ' + endpoint.strip() + ' ' + 'ip'
                app.send.publish(option, message)
        else:
            #ip_range = ip.split('/')
            #filepath = '/tools/output/' + domain + '/ipscan/' + ip_range[0] + '_' + ip_range[1]
            for IP in IPNetwork(ip):
                option = 'ip-scan'
                message = option + ' ' + str(IP) + ' ' + domain + ' ' + date
                app.send.publish(option, message)

def on_message(ch, method_frame, _header_frame, body, args):
    (conn, thrds) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(conn, ch, delivery_tag, body))
    t.start()
    thrds.append(t)


def rabbitmqConnection(options):
    while True:
        connection = app.connection.connectionPack()
        channel = connection.channel()
        channel.exchange_declare(
            exchange='test',
            exchange_type='direct',
            passive=False,
            durable=True,
            auto_delete=False)

        for scan_type in options:
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
