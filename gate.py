#!/usr/bin/env python

import zmq
import argparse
from threading import Thread
import socket

__debug = False
QUEUE_PORT=5000
SOCK_PORT=10001

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
    SOCK_PORT=10002
    if __debug:
        print("DEBUG: Sock port is changed on %i" % (SOCK_PORT))

context = zmq.Context()
queue = context.socket(zmq.PUB)
queue.bind("tcp://0.0.0.0:%i" %(QUEUE_PORT))


def send(text):
    """ Send to all string text """
    if __debug:
        print("DEBUG: send(%s)" % (text))
    queue.send(text)


def gate_sock():
    """ gate sock -> queue. No args """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("0.0.0.0", SOCK_PORT))
    srv.listen(1)
    while True:
        s, addr = srv.accept()
        if __debug:
            print("DEBUG: sock connection from", addr)
        # TODO: despatch open socks in separate thread?
        data = s.recv(1024)
        if __debug:
            print("DEBUG: sock recv: %s" % (data))
        print("data[:4] = %s" % (data[:4]))
        if data[:4] == 'msg ':
            print("DEBUG: sock recv msg type. Send it to queue")
            send(data[4:])

gate_sock()
