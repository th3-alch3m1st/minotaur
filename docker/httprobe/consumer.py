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
    subdomain = opt[1]
    domain = opt[2]
    date = opt[3]

    filepath = '/tools/output/' + domain
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if opt[0] == 'alive':

        with open(filepath + '/alive-' + domain + '.' + date, 'ab') as out:
            httprobe_process = Popen(['/go/bin/httprobe', '-p', 'xlarge', '-c', '150', '-t', '15000'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            httprobe_stdout = httprobe_process.communicate(subdomain)[0]
            endpoints = httprobe_stdout.split()
            for endpoint in endpoints:
                option = 'dir-scan'
                message = option + ' ' + endpoint + ' ' + 'domain'
                app.send.publish(option, message)

                option = 'httpx'
                message = option + ' ' + endpoint + ' ' + domain + ' ' + date
                app.send.publish(option, message)

                option = 'nuclei'
                message = option + ' ' + endpoint + ' ' + domain + ' ' + date
                app.send.publish(option, message)

                out.write("%s\n" % endpoint)

            # Send to screenshots
            option = 'screenshots'
            message = option + ' ' + domain + ' ' + date
            app.send.publish(option, message)

    elif opt[0] == 'httpx':

        with open(filepath + '/httpx-' + domain + '.' + date, 'ab') as out:
            httpx_process = Popen(['/go/bin/httpx', '-retries', '4', '-title', '-content-length', '-status-code', '-follow-redirects', '-silent'], stdin=PIPE, stdout=out, stderr=STDOUT)
            httpx_process.communicate(subdomain)[0]
            httpx_process.wait()
            #out.write("%s\n" % result)

    elif opt[0] == 'nuclei':

        filepath = '/tools/output/' + domain + '/nuclei'
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        templates = ['cves', 'files', 'panels', 'security-misconfiguration', 'subdomain-takeover', 'technologies', 'tokens', 'vulnerabilities', 'workflows']
        for template in templates:
            template_file = '/tools/input/nuclei-templates/' + template + '/' + '*.yaml'
            with open(filepath + '/nuclei-' + template + '-' + domain + '.' + date, 'ab') as out:
                nuclei_process = Popen(['/go/bin/nuclei', '-target', subdomain, '-t', template_file, '-c', '151', '-retries', '3', '-timeout', '10', '-silent'], stdout=out, stderr=STDOUT)
                nuclei_process.communicate()[0]
                nuclei_process.wait()

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
