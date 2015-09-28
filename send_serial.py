#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import argparse
import signal
import urllib
from time import sleep
import sys

from arduino import Arduino

__debug = False
QUEUE_PORT = 5000
REP_PORT=6000

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
    debug_print("DEBUG: No need to set --test for gate_serial")
    REP_PORT=6001
    debug_print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"ard")

ard = Arduino('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A80090sP-if00-port0',
              debug=__debug)
while True:
    data = sub.recv()
    debug_print("Recieved: " + data);
    cmd = data[4:]
    debug_print("Command: " + data);
    ard.write(cmd)
