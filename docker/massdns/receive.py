#!/usr/bin/env python
'''
    This is the subscriber

'''
import pika
import sys,os
import time
import app.spawn_subscriber
from datetime import datetime
from subprocess import Popen, PIPE

options = sys.argv[1:]
if not options:
    sys.stderr.write("Usage: %s [passive] [brute] [perms]\n" % sys.argv[0])
    sys.exit(1)

def callback(ch, method, properties, body):
    opt = body.split(" ")
    print(" [x] Starting %r scans for %r" % (method.routing_key, opt[1]))

    # Grab date and add to filename
    now = datetime.now()
    date = now.strftime("%Y%m%d%H%M%S")

    # Check if folder exists
    filepath = '/tools/output/brute-force'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Start scan
    if method.routing_key == 'brute':
        print("Start massdns")
        filename = filepath + '/brute-force-' + opt[1] + '.' + opt[2]
        with open(filename, 'wb') as out:
            subbrute_process = Popen(['/tools/massdns/scripts/subbrute.py', '/tools/input/alldns.txt', opt[1]], stdout=PIPE)
            massdns_process = Popen(['/bin/massdns', '-r', '/tools/input/resolvers.txt', '-t', 'A', '-o' , 'S'], stdin=subbrute_process.stdout, stdout=out)
            subbrute_process.stdout.close()
            massdns_process.communicate()[0]
            massdns_process.wait()
            out.flush()
            os.fsync(out)
            out.close()

        if os.stat(filename).st_size == 0:
            os.remove(filename)
        else:
            clean_filename = filename + '-cleaned'
            with open(clean_filename, 'wb') as clean_file:
                clean_process = Popen(['/tools/fresh.py/clean.sh', filename], stdout=clean_file)
                clean_process.wait()
                clean_file.flush()
                os.fsync(clean_file)
                clean_file.close()
            if os.stat(clean_filename).st_size == 0:
                os.remove(clean_filename)
            os.remove(filename)
        print("finished massdns")
    elif method.routing_key == 'resolve':
        print("Start massdns")
        perms_file = '/tools/output/permutations/permutations-' + opt[1] + '.' + opt[2]
        input_file = open(perms_file, 'rb')
        with open(perms_file + '-resolved', 'wb') as out:
            massdns_process = Popen(['/bin/massdns', '-r', '/tools/input/resolvers.txt', '-t', 'A', '-o' , 'S'], stdin=input_file, stdout=out)
            massdns_process.communicate()[0]
            out.flush()
            os.fsync(out)
            out.close()
        if os.stat(perms_file + '-resolved').st_size == 0:
            os.remove(perms_file + '-resolved')
        else:
            clean_filename = perms_file + '-resolved' + '-cleaned'
            with open(clean_filename, 'wb') as clean_file:
                clean_process = Popen(['/tools/fresh.py/clean.sh', perms_file + '-resolved'], stdout=clean_file)
                clean_process.wait()
                clean_file.flush()
                os.fsync(clean_file)
                clean_file.close()

            if os.stat(clean_filename).st_size == 0:
                os.remove(clean_filename)
            os.remove(perms_file + '-resolved')
        os.remove(perms_file)

        print("finished massdns")

app.spawn_subscriber.rabbitmqConnection(options, callback)
