#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import zmq
import signal
import argparse

from sound import Ultra

QUEUE_PORT = 5000

def debug_print(text):
    if __debug:
        print("DEBUG: ", text)

argparser = argparse.ArgumentParser()
argparser.add_argument('--debug', help='enable debug mode', action='store_true')
argparser.add_argument('--tests', help='change ports on test ports', action='store_true')
args = argparser.parse_args()
if args.debug:                  # --debug
    print("DEBUG: Enabled debug mode.")
    __debug = True
if args.tests:                  # --tests
    QUEUE_PORT=5001
    debug_print("DEBUG: Queue port is changed on %i" % (QUEUE_PORT))

ultra = Ultra()
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"msg")

def signal_handler(signal, frame):
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def dispatch_msg(data):
    try:
        args = data.split(' ')
        if args[1] == 'radio':
            debug_print("run ultra")
            ultra.switch()
    except Exception  as e:
        print "ERROR: on parse msg: %\n%s" % (data, e)

while True:
    try:
        data = sub.recv()
        debug_print("Recieved: %s" % (data))
        if data.split(' ')[0] == 'msg':
            dispatch_msg(data)
    except KeyboardInterrupt:
                signal_handler("KeyboardInterrupt", "")
