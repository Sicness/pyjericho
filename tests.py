import unittest
import zmq
import socket
from threading import Thread
from time import sleep

QUEUE_PORT = 5001
SOCK_PORT = 10002
REP_PORT = 6001

context = zmq.Context()
sub = context.socket(zmq.SUB)

def send_test_sock():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", SOCK_PORT))
    s.send("msg test message")
    s.close()


def send_test_zmq():
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:%i" % (REP_PORT))
    sleep(0.2)
    socket.send("msg zmq test message")


print("Hello, let's get started")

sub.connect("tcp://127.0.0.1:%i" % (QUEUE_PORT))


class Test(unittest.TestCase):
    def test_sock2queue(self):
        sock_thr = Thread(target = send_test_sock, args = ())
        sub.setsockopt(zmq.SUBSCRIBE,"")
        sock_thr.start()
        #print sub.recv()
        self.assertEqual(sub.recv(),"msg test message")

    def test_zmq2queue(self):
        sock_thr = Thread(target = send_test_zmq, args = ())
        sock_thr.start()
        self.assertEqual(sub.recv(), "msg zmq test message")


if __name__ == "__main__":
        unittest.main()

gate_proc.terminate()
