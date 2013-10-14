#!/usr/bin/env python

import zmq
import argparse

QUEUE_PORT=5000
REP_PORT=6000

__debug = False

argparser = argparse.ArgumentParser()
argparser.add_argument('--debug', help='enable debug mode', action='store_true')
argparser.add_argument('--tests', help='change ports on test ports', action='store_true')
args = argparser.parse_args()
if args.debug:                  # --debug
    print("DEBUG: Enabled debug mode.")
    __debug = True
if args.tests:                  # --tests
    QUEUE_PORT=5001
    if __debug:
        print("DEBUG: Queue port is changed on %i" % (QUEUE_PORT))
    REP_PORT=6001
    if __debug:
        print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))

context = zmq.Context()
queue = context.socket(zmq.PUB)
queue.bind("tcp://0.0.0.0:%i" %(QUEUE_PORT))

sock = context.socket(zmq.REP)
sock.bind("tcp://0.0.0.0:%i" % (REP_PORT))
while True:
    data = sock.recv()
    if __debug:
        print("DEBUG: recieved: %s" % (data))
    if data[:4] == 'msg ':
        if __debug:
            print("DEBUG: send(%s)" % (data))
        queue.send(data)
        sock.send("OK")
    else:
        sock.send("ERR")
