import serial


class Arduino:
    def __init__(self, adr, onFound = None, onLost = None, baudrate = 9600, debug = False):
	self.debug = debug
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
                    self.debug_print("Loose connection with Serail %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                    if self.onLost != None:
                        self.onLost()
                elif self._connected == None:
                    self.debug_print("Can't open seril port %s:%s %s" % (self.adr, self.baudrate, sys.exc_info()[0]))
                self._connected = False
                sleep(5)
                continue

            # Success conntect to serial
            self.debug_print('Recconnectred to Serail %s:%s' % (self.adr, self.baudrate))
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
                self.debug_print("Can't read from serial: %s" % sys.exc_info()[0])
                self.connect()
                continue
            break
        return line[:-2]

    def write(self, msg):
	msg = msg + '\0'
	try:
	    self.s.write(msg.encode())
	except serial.SerialException:
                self.debug_print("Can't write to serial: %s" % sys.exc_info()[0])
                self.connect()

    def debug_print(self, text):
        if self.debug:
            print("DEBUG: ", text)
