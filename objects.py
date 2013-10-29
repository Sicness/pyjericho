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

    def motion_triger(self, state):
        if self.auto:
            if state:
                self.on()
            else:
                self.off()
