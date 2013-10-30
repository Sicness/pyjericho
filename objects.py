import noolite

class NooLight:
    def __init__(self, ch, auto=False, sn=0):
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
        self._noolite.set(self.ch)

    def set_auto(self, auto):
        if not isinstance(mode, bool):
            print "WARRING: noolite set_auto should take bool! exit"
            return
        self.auto = auto

    def motion_triger(self, state):
        if self.auto:
            if state:
                self.on()
            else:
                self.off()
