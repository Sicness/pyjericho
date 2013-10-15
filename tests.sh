#!/bin/bash
echo "*** Run instanses ***"
python ./pipeline.py --test &
python ./gate_sock.py --tests &
echo "*** Wait for instanses execution ***"
sleep 1
echo "*** Run tests ***"
python ./tests.py
echo "*** Kill them all ***"
kill %1
kill %2
