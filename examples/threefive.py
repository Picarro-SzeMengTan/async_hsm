#!/usr/bin/env python3

import farc


class Three(farc.Ahsm):
    @farc.state
    def _initial(self, event):
        print("Three _initial")
        self.te = farc.TimeEvent("TICK3")
        return self.tran(self._running)

    @farc.state
    def _running(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("three enter")
            self.te.postEvery(self, 3)
            return self.handled(event)

        elif sig == farc.Signal.TICK3:
            print("three tick")
            return self.handled(event)

        elif sig == farc.Signal.EXIT:
            print("three exit")
            self.te.disarm()
            return self.handled(event)

        return self.super(self.top)


class Five(farc.Ahsm):
    @farc.state
    def _initial(self, event):
        print("Five _initial")
        self.te = farc.TimeEvent("TICK5")
        return self.tran(self._running)

    @farc.state
    def _running(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            print("five enter")
            self.te.postEvery(self, 5)
            return self.handled(event)

        elif sig == farc.Signal.TICK5:
            print("five tick")
            return self.handled(event)

        elif sig == farc.Signal.EXIT:
            print("five exit")
            self.te.disarm()
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    # Uncomment this line to get a visual execution trace (to demonstrate debugging)
    # from farc.SimpleSpy import SimpleSpy
    # farc.Spy.enable_spy(SimpleSpy)

    three = Three()
    five = Five()

    three.start(3)
    five.start(5)

    farc.run_forever()
