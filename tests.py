import unittest
import subprocess
import zmq
import socket
from threading import Thread
from time import sleep

QUEUE_PORT = 5001
SOCK_PORT = 10002

context = zmq.Context()
sub = context.socket(zmq.SUB)

def send_test_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", SOCK_PORT))
    s.send("msg test message")
    s.close()


print("Hello, let's get started")
print("Run gate.py in tests mode")

gate_proc = subprocess.Popen(('./gate.py', '--tests'))
print("Waiting 2 secs for gate.py start")
sleep(2)


class Test(unittest.TestCase):
    def test_sock2queue(self):
        sock_thr = Thread(target = send_test_sock, args = ())
        sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))
        sub.setsockopt(zmq.SUBSCRIBE,"")
        sock_thr.start()
        #print sub.recv()
        self.assertEqual(sub.recv(),"test message")

if __name__ == "__main__":
        unittest.main()

gate_proc.terminate()
