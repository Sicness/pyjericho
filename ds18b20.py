#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import argparse
import signal
from time import sleep
import sys

__debug = False
#QUEUE_PORT = 5000
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
    #QUEUE_PORT=5001
    #debug_print("DEBUG: Queue port is changed on %i" % (QUEUE_PORT))
    REP_PORT=6001
    debug_print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

context = zmq.Context()
#sub = context.socket(zmq.SUB)
#sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
#sub.setsockopt(zmq.SUBSCRIBE,"ard")
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))
class ds18b20:
    def __init__(self, adr):
        self.__dev_adr = adr

    def read_temp_raw(self):
        try:
            f = open(self.__dev_adr, 'r')
        except:
            raise
        lines = f.readlines()
        f.close()
        return lines

    def read_c(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def read_f(self):
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_f

    def read_temp(self):
        """ Read temperature from sensor
        and return turpe (c, f) """
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

ds = ds18b20('/sys/bus/w1/devices/10-0008025b6d03/w1_slave')
while True:
    try:
        data = ds.read_c()
        debug_print("Read c: %s" % (data))
        req.send('temp ds18b20 %s' % (data))
        req.recv()
        sleep(15)
    except KeyboardInterrupt:
            signal_handler("KeyboardInterrupt", "")
