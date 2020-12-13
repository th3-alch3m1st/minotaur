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

    opt = body.split(" ")
    domain = opt[1]
    date = opt[2]

    if opt[0] == 'wildcard':
        subdomains_file = str('/tools/output/' + domain + '/new_subdomains-' + domain + '.' + date)
        with open('/tools/output/' + domain + '/subdomains-resolved-' + domain + '.' + date, 'wb') as resolved_subdomains_file:
            shuffledns_process = Popen(['/go/bin/shuffledns', '-d', domain, '-list', subdomains_file, '-r', '/tools/input/resolvers.txt', '-silent'], stdout=resolved_subdomains_file)
            shuffledns_process.communicate()[0]
            shuffledns_process.wait()

    '''
    if opt[0] == 'wildcard':
        resolved_subdomains = []
        resolved_subdomains_file = open('/tools/output/' + domain + '/subdomains-resolved-' + domain + '.' + date, 'wb')
        with open('/tools/output/' + domain + '/subdomains-' + domain + '.' + date, 'rb') as subdomains_file:
            for subdomain in subdomains_file:
                subdomain = subdomain.rstrip('\n')
                subdomain_array = subdomain.split('.')
                if len(subdomain_array) > 2:
                    p1 = Popen(['dig', '@1.1.1.1', 'A,CNAME', subdomain, '+short'], stdout=PIPE)
                    subdomain_ip_address, err1 = p1.communicate()
                    for i in range(1, len(subdomain_array)-1):
                        wildcard = '*.'+'.'.join(map(str, subdomain_array[i:]))
                        p2 = Popen(['dig', '@1.1.1.1', 'A,CNAME', wildcard, '+short'], stdout=PIPE)
                        wildcard_ip_address, err2 = p2.communicate()
                        if subdomain_ip_address != wildcard_ip_address:
                            #resolved_subdomains.append(subdomain)
                            resolved_subdomains_file.write("%s\n" % subdomain)
                            break
                elif subdomain == domain:
                    resolved_subdomains_file.write("%s\n" % subdomain)

        resolved_subdomains_file.close()
    '''

    with open('/tools/output/' + domain + '/subdomains-resolved-' + domain + '.' + date) as resolved_subdomains:
        for subdomain in resolved_subdomains:
            option = 'alive'
            message = option + ' ' + subdomain.rstrip() + ' ' + domain + ' ' + date
            app.send.publish(option, message)

    cb = functools.partial(ack_message, ch, delivery_tag)
    conn.add_callback_threadsafe(cb)

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
