# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import threading
import tldextract
from datetime import datetime
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

    opt = body.decode().split(" ")
    url_to_scan = opt[1]
    ip_domain = opt[2]

    url = tldextract.extract(url_to_scan)
    if ip_domain == 'domain':
        # Case of url being similar to https://www.example.com:8443/
        subPath = "{}.{}.{}".format(url.subdomain, url.domain, url.suffix)
        domPath = "{}.{}".format(url.domain, url.suffix)
    elif ip_domain == 'ip':
        # Case of url being similar to https://8.8.8.8:8443/
        subPath = url.domain
        domPath = 'ip-scans'

    if opt[0] == 'dir-scan':

        filepath = '/tools/output/dirsearch/' + domPath + '/' + subPath
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        now = datetime.now()
        filename = now.strftime("%d-%m-%Y_%H-%M-%S")

        #~/tools/ffuf -w ~/lists/0.the-one-to-use.txt -u https://prod-8x8-latency.8x8.vc/FUZZ -H 'Host: localhost' -ac -t 600
        ffufFile = 'ffuf_' + filename + '.html'
        ffuf_process = Popen(['/go/bin/ffuf', '-w', '/tools/input/vhosts-wordlist.txt', '-u', url_to_scan + '/FUZZ', '-H', 'Host: localhost', '-ac', '-t', '300', '-o', filepath + '/' + ffufFile, '-of' , 'html'], stderr=STDOUT)
        ffuf_process.communicate()[0]
        ffuf_process.wait()

        dirsearch_process = Popen(['/tools/dirsearch/dirsearch.py', '-w', '/tools/input/wordlist.txt', '-url', url_to_scan, '--random-agent', '-e', '.php,.asp,.aspx,.jsp,.js,.ini,.html,.log,.txt,.sql,.zip,.tar.gz,.rar,.conf,.cgi,.json,.jar,.dll,.xml,.db,.py,.ashx,,/', '-x', '400,429,501,503,520', '-t', '300', '--plain-text-report=' + filepath + '/' + filename], stderr=STDOUT)
        dirsearch_process.communicate()[0]
        dirsearch_process.wait()

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
