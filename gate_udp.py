#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import argparse
import signal
import urllib
from time import sleep
import sys
from socket import *

__debug = False
QUEUE_PORT = 5000
REP_PORT = 6000
BROAD_PORT = 11000
BROAD_NET = '192.168.2.255'

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
    REP_PORT=6001
    debug_print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))
    REP_PORT=11001
    debug_print("DEBUG: UDP broadcat port is changed on %i" % (REP_PORT))

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"")
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))
udp = socket(AF_INET, SOCK_DGRAM)
udp.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

def send(text):
    udp.sendto(text, (BROAD_NET, BROAD_PORT))

while True:
    data = sub.recv()
    debug_print('Resend: %s' % (data))
    send(data)
