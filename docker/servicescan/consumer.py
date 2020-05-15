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

    opt = body.decode().split(" ")
    ip = str(opt[1])
    date = opt[2]

    if opt[0] == 'service-scan':

        if ip.find('/') == -1:
        # ip format is 8.8.8.8

            filepath = '/tools/output/ipscan/' + ip
            masscan_result = open(filepath + '/scan_' + date, 'rb')
            results = masscan_result.readlines()

            ports = '21'
            for res in results:
                #Timestamp: 1587900582   Host: 192.84.16.163 ()  Ports: 80/open/tcp//http//
                if 'Timestamp' in res:
                    format_res = (res.strip()).split(" ")
                    host = format_res[2]
                    port = format_res[4].split('/')[0]
                    ports += ',' + port

                nmap_process = Popen(['nmap', '-sSV', host, '-p', ports ], stdout=STDOUT, stderr=STDOUT)
                nmap_process.communicate()[0]
                nmap_process.wait()

        else:
        # ip format is 8.8.8.8/24

            filepath = '/tools/output/ipscan/' + ip
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            fileoutput = str(filepath + '/scan_' + date)
            masscan_process = Popen(['/tools/masscan/bin/masscan', '-p1-65535', ip, '--max-rate', '1000', '-oG', fileoutput], stdout=STDOUT, stderr=STDOUT)
            masscan_process.communicate()[0]
            masscan_process.wait()

    cb = functools.partial(ack_message, ch, delivery_tag)
    conn.add_callback_threadsafe(cb)

    # nmap-scan subnet_24 date / nmap-scan ip date
    #option = 'nmap-scan'
    #message = option + ' ' + ip + ' ' + date
    #app.send.publish(option, message)


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
