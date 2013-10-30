#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import zmq
import signal
import argparse
import traceback

import objects

from sound import Ultra

QUEUE_PORT = 5000
__debug = False

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
sub.setsockopt(zmq.SUBSCRIBE,"")

def signal_handler(signal, frame):
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

light_hole = objects.NooLight(0, auto=False, sn=1)

def on_motion(where, state):
    debug_print("Applicated motion in %s" % (where))
    if where == 'hole':
        light_hole.motion_triger(state)

def noolite_hole_set_auto():
    debug_print("Enable auto mode for Light in hole")
    light_hole.set_auto(True)

def noolite_hole_set_on():
    debug_print("Disble auto mode for Light in hole and light ON")
    light_hole.set_auto(False)
    light_hole.on()

def noolite_hole_set_off():
    debug_print("Disble auto mode for Light in hole and light OFF")
    light_hole.set_auto(False)
    light_hole.off()

IR_codes = dict()
def init_IR_codes():
    """ Bind functions on IR codes """
    #IR_codes.update( {b'FF629D' : say_temp} )     # Say temperature status
    #IR_codes.update( {b'FFA857' : volume_inc} )   # increase volume
    #IR_codes.update( {b'FFE01F' : volume_dec} )   # reduce volume
    #IR_codes.update( {b'FF906F' : toSecureMode} )       # Will be noBodyHome
    IR_codes.update( {b'FFC23D' : ultra.switch} )       # On/off radio
    IR_codes.update( {b'BF09C35C' : ultra.switch} )     # On/off radio (big)
    #IR_codes.update( {b'8BE68656' : holeNightLightAuto} )
    #IR_codes.update( {b'B21F28AE' : hole_night_light.setManualStateOff} )
    #IR_codes.update( {b'A6B1096A' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'24014B0' : noolite_hole_set_auto} )
    IR_codes.update( {b'8FC212DB' : noolite_hole_set_off} )
    IR_codes.update( {b'7960556F' : noolite_hole_set_on} )
    #IR_codes.update( {b'FF10EF' : holeNightLightAuto} )
    #IR_codes.update( {b'FF38C7' : hole_night_light.setManualStateOff} )
    #IR_codes.update( {b'FF5AA5' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'FF30CF' : noolite_hole_set_auto} )
    IR_codes.update( {b'FF18E7' : noolite_hole_set_off} )
    IR_codes.update( {b'FF7A85' : noolite_hole_set_on} )

init_IR_codes()

def dispatch_msg(data):
    try:
        args = data.split(' ')
        if args[1] == 'radio':
            debug_print("run ultra")
            ultra.switch()
        # msg Motion in room YES
        if args[1] == 'Motion' and args[2] == 'in':
            on_motion(args[3], 1 if args[4] == 'YES' else 0)
    except Exception  as e:
        print "ERROR: on parse msg: %s | %s" % (data, e)
        traceback.print_exc(file=sys.stdout)

def dispatch_pub(data):
    try:
        args = data.split(' ')
        if args[0] == 'temp':
            debug_print(args)
            ultra.switch()
        if args[0] == 'IR':
            if args[1] in IR_codes:
                IR_codes[args[1]]()
    except Exception  as e:
        print "ERROR: on parse msg: %s\n%s" % (data, e)

while True:
    try:
        data = sub.recv()
        debug_print("Recieved: %s" % (data))
        if data.split(' ')[0] == 'msg':
            dispatch_msg(data)
        else:
            dispatch_pub(data)
    except KeyboardInterrupt:
                signal_handler("KeyboardInterrupt", "")

