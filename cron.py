#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import signal
import traceback
from datetime import datetime
from time import sleep
import sys

import zmq

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
    debug_print("DEBUG: Queue port is changed on %i" % (QUEUE_PORT))
    REP_PORT=6001
    debug_print("DEBUG: REP port is changed on %i" % (QUEUE_PORT))

def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"cron set")
sub.setsockopt(zmq.SUBSCRIBE,"cron add")
sub.setsockopt(zmq.SUBSCRIBE,"cron list")
sub.setsockopt(zmq.SUBSCRIBE,"cron rm")
sub.setsockopt(zmq.SUBSCRIBE,"cron del")
poller = zmq.Poller()
poller.register(sub, zmq.POLLIN)
req = context.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:%i" % (REP_PORT))

tasks = dict()

def send(msg_type, text):
    data = " ".join(["cron", msg_type, text])
    debug_print("send: %s" % (data))
    req.send(data)
    req.recv()

while True:
    try:
        x = poller.poll(800)    # wait for a zmq msg for 800 msg
        if len(x) > 0:          # If we just recved a msg
            data = sub.recv()   # take it
            # Applicate the msg
            debug_print("Recieved: %s" % (data))
            args = data.split(' ')
            cmd = args[1]
            if cmd == 'set' or cmd == 'add':
                when, name = datetime.fromtimestamp(float(args[2])), args[3]
                debug_print("add task %s AT %s" % (name, when))
                tasks[name] = when
            elif cmd == 'list':
                debug_print("command 'list' recieved; Tasks:")
                for i,j in tasks.iteritems():
                    send('has', "%s AT %s" % (i, j))
            elif cmd == 'rm' or cmd == 'del':
                debug_print("rm '%s' task" % (args[2]))
                tasks.pop(args[2], None)
        else:
            # No new msg. Check cron tasks
            now = datetime.now()
            rm_list = list()            # tasks for deletion
            for name, when in tasks.iteritems():
                if now > when:
                    send('event', name)   # Task happaned
                    # mark the task as must be deleted
                    rm_list.append(name)
            for task in rm_list:
                tasks.pop(task, None)   # Delete from task list
                debug_print("task %s is deleted" % (name))


    except KeyboardInterrupt:
        signal_handler("KeyboardInterrupt", "")
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        print("ERROR: ", e)
