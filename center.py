#!/usr/bin/python
# -*- coding: UTF-8 -*-

import zmq
import signal
import argparse
import traceback
import time
from datetime import datetime, timedelta
import sys, traceback

import objects

from sound import Ultra

QUEUE_PORT = 5000
REP_PORT=6000
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
    REP_PORT=6001
    debug_print("DEBUG: Zmq replay port is changed on %i" % (REP_PORT))

glob = dict()
ultra = Ultra()
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"")
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))

def signal_handler(signal, frame):
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


lights = dict()
lights['hole'] = objects.NooLight(0, auto=False, sn=1)  # sm - watm light
lights['room'] = objects.NooLight(1, auto=False, sn=1)  # sm - watm light
lights['bathroom'] = objects.NooLight(3, auto=False)
lights['kitchen'] = objects.NooLight(2, auto=False)

def now():
    return datetime.now()

def nowStr(time=None):
    """ now -> str
    time is datedate.datetime.now.time() """
    if time is None:
        time = datetime.now().time()
    if time.minute < 10:
        return time.strftime("%H ноль %m")
    else:
        return time.strftime("%H %M")

def send(text):
    req.send(text)
    req.recv()

def say(text):
    req.send(b"say %s" % (text))
    req.recv()

def on_motion(where, state):
    debug_print("Applicated motion in %s" % (where))
    if where == 'hole':
        lights['hole'].motion_triger(state)
        if 'secureMode' in glob and glob['secureMode']:
            glob['secureMode'] = False
            wellcomeHome()
    elif where in lights:
        debug_print("Applicated motion in %s" % (where))
        lights[where].motion_triger(state)

def noolite_hole_set_auto():
    debug_print("Enable auto mode for Light in hole")
    lights['hole'].set_auto(True)

def noolite_hole_set_on():
    debug_print("Disble auto mode for Light in hole and light ON")
    lights['hole'].set_auto(False)
    lights['hole'].on()

def noolite_hole_set_off():
    debug_print("Disble auto mode for Light in hole and light OFF")
    lights['hole'].set_auto(False)
    lights['hole'].off()

def cronAdd(name, when):
    debug_print("set to cron %s AT %s" % (name, when))
    send(" ".join(["cron add", str(time.mktime(when.timetuple())), name]))

def say_temp():
    debug_print("Gonna say hole_ds_18b20")
    if 'hole_ds18b20' in glob:
        say("Температура дома %f" % (glob['hole_ds18b20']))


def toSecureMode():
    cronAdd('toSecureMode', now() + timedelta(minutes=1))
    say('Сторожевой режим будет включен через одну минуту. Приятного время препровождения!')

def secureMode():
    glob['secureMode'] = True
    debug_print("Secure mode is enabled")

def wellcomeHome():
    say("Добро пожаловать домой.")
    say("Текущее время " + nowStr())
    say_temp()



IR_codes = dict()
def init_IR_codes():
    """ Bind functions on IR codes """
    IR_codes.update( {b'FF629D'   : say_temp} )     # Say temperature status
    IR_codes.update( {b'84FF9375' : say_temp} )     # Say temperature status
    #IR_codes.update( {b'FFA857' : volume_inc} )   # increase volume
    #IR_codes.update( {b'FFE01F' : volume_dec} )   # reduce volume
    IR_codes.update( {b'FF906F'   : toSecureMode} )       # Will be noBodyHome
    IR_codes.update( {b'FFC23D'   : ultra.switch} )       # On/off radio
    IR_codes.update( {b'BF09C35C' : ultra.switch} )     # On/off radio (big)
    #IR_codes.update( {b'8BE68656' : holeNightLightAuto} )
    #IR_codes.update( {b'B21F28AE' : hole_night_light.setManualStateOff} )
    #IR_codes.update( {b'A6B1096A' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'24014B0'  : noolite_hole_set_off} )
    IR_codes.update( {b'8FC212DB' : noolite_hole_set_on} )
    IR_codes.update( {b'7960556F' : noolite_hole_set_auto} )
    #IR_codes.update( {b'FF10EF' : holeNightLightAuto} )
    #IR_codes.update( {b'FF38C7' : hole_night_light.setManualStateOff} )
    #IR_codes.update( {b'FF5AA5' : hole_night_light.setManualStateOn} )
    IR_codes.update( {b'FF30CF'  : noolite_hole_set_off} )
    IR_codes.update( {b'FF18E7'  : noolite_hole_set_on} )
    IR_codes.update( {b'FF7A85'  : noolite_hole_set_auto} )

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
    global temp
    try:
        args = data.split(' ')
        if args[0] == 'temp' and args[1] == 'ds18b20':
            debug_print("found a value for hole_ds18b20")
            try:
                glob['hole_ds18b20'] = "%.1f" % (float(args[2]))
            except:
                print "WARNING: temp ds18b20 _float_"

        elif args[0] == 'IR':
            if args[1] in IR_codes:
                IR_codes[args[1]]()

        elif args[0] == 'light':
            room, cmd = args[1], args[2]
            if room in lights:
                debug_print('work with %s light' % (room))
                if cmd == 'on':
                    lights[room].on()
                elif cmd == 'off':
                    lights[room].off()
                elif cmd == 'switch':
                    lights[room].switch()
                elif cmd == 'set':
                    lights[room].set(args[3])
                elif cmd == 'auto':
                    lights[room].set_auto(True)
                elif cmd == 'noauto':
                    lights[room].set_auto(False)

        elif args[0] == 'cron' and args[1] == 'event':
            env = args[2]
            debug_print("Cron event " + env)
            if env == 'toSecureMode':
                secureMode()
    except Exception  as e:
        traceback.print_exc(file=sys.stderr)
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

