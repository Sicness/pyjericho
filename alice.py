#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import mplayer
import argparse

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

QUEUE_PORT = 5000
user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64) "
              "AppleWebKit/537.17 "
              "(KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17")

player = mplayer.Player(args=('-user-agent', user_agent))  #, '-ao', 'pulse'))
player.cmd_predix = ''

context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
sub.setsockopt(zmq.SUBSCRIBE,"say")

def say(text, lang = "ru"):
        url = url = (u"http://translate.google.com/"
                    u"translate_tts?tl={0}&q={1}".format(
                    lang, urllib.quote(text)))
        player.loadfile(url, 1)

while True:
    try:
        data = sub.recv()
        debug_print("Recieved: %s" % (data))
        say(data.split(' ')[1:])
    except KeyboardInterrupt:
                signal_handler("KeyboardInterrupt", "")
