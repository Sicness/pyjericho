import noolite

class NooLight:
    def __init__(self, ch, auto=False, sn=0):
        # sn - warm light
        self._noolite = noolite.NooLite()
        self.auto = auto
        self.ch = ch
        self.sn = sn
        self.state = 0

    def on(self):
        self._noolite.on(self.ch)

    def off(self):
        self._noolite.off(self.ch)

    def set(self, value):
        if self.sn == 0:
            return
        self._noolite.set(self.ch, value)

    def switch(self):
        self._noolite.switch(self.ch)

    def set_auto(self, auto):
        if not isinstance(auto, bool):
            print "WARRING: noolite set_auto should take bool! exit"
            return
        self.auto = auto
        if auto:
            if self.state:
                self.on()
            else:
                self.off()

    def motion_triger(self, state):
        self.state = state
        if self.auto:
            if state:
                self.on()
            else:
                self.off()
