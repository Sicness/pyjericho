#!/usr/bin/env python


import zmq
import argparse
from threading import Thread
import socket

__debug = False
SOCK_PORT=10001
REP_PORT=6000

# ARGUMENT PARSER
argparser = argparse.ArgumentParser()
argparser.add_argument('--debug', help='enable debug mode', action='store_true')
argparser.add_argument('--tests', help='change ports on test ports', action='store_true')
args = argparser.parse_args()
if args.debug:                  # --debug
    print("DEBUG: Enabled debug mode.")
    __debug = True
if args.tests:                  # --tests
    SOCK_PORT=10002
    if __debug:
        print("DEBUG: Sock port is changed on %i" % (SOCK_PORT))
    REP_PORT=6001
    if __debug:
        print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))

# CONNECTION WITH THE QUEUE
context = zmq.Context()
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))

# RESEND SOCK -> QUEUE
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
    try:
        req.send(data)
    except zmq.error.ZMQError as e:
        print("ERROR: can't send to queue: %s" % (e))
    # TODO: Dispatch replay
    req.recv()
    s.close()
