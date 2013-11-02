#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import serial
import argparse
import signal
import urllib
from time import sleep
import sys

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
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))

class Arduino:
    def __init__(self, adr, onFound = None, onLost = None, baudrate = 9600):
        self.adr = adr
        self.baudrate =  baudrate
        self.onFound = onFound
        self.onLost  = onLost
        self._connected = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.s = serial.Serial(self.adr, self.baudrate, timeout=2)
            except:
                if self._connected == True:
                    debug_print("Loose connection with Serail %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                    if self.onLost != None:
                        self.onLost()
                elif self._connected == None:
                    debug_print("Can't open seril port %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                self._connected = False
                sleep(5)
                continue

            # Success conntect to serial
            debug_print('Recconnectred to Serail %s:%s' % (self.adr, self.baudrate))
            if self._connected == False:
                if self.onFound != None:
                    self.onFound()
            self._connected = True
            break

    def read(self):
        """ Read line from Serial with out \r\n """
        while True:
            try:
                line = self.s.readline()
                if not line:
                    continue
            except serial.SerialException:
                debug_print("Can't read from serial: %s" % sys.exc_info()[0])
                self.connect()
                continue
            break
        return line[:-2]

def onArdFound():
    req.send("msg arduino is found")
    req.recv()

def onArdLost():
    req.send("msg arduino is lost")
    req.recv()

ard = Arduino('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A80090sP-if00-port0',
              onFound=onArdFound, onLost=onArdLost)
while True:
    try:
        debug_print("Arduino reading...")
        data = ard.read()
        debug_print("Arduino read: %s" % (data))
        if data.split(' ')[0] == 'IR':
            req.send('%s' % (data))
            req.recv()
        else:
            req.send('msg %s' % (data))
            req.recv()
    except KeyboardInterrupt:
            signal_handler("KeyboardInterrupt", "")
