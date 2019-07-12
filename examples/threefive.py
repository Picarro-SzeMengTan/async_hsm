#!/usr/bin/env python3

import async_hsm


class Three(async_hsm.Ahsm):
    @async_hsm.state
    def _initial(self, event):
        print("Three _initial")
        self.te = async_hsm.TimeEvent("TICK3")
        return self.tran(self._running)

    @async_hsm.state
    def _running(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("three enter")
            self.te.postEvery(self, 3)
            return self.handled(event)

        elif sig == async_hsm.Signal.TICK3:
            print("three tick")
            return self.handled(event)

        elif sig == async_hsm.Signal.EXIT:
            print("three exit")
            self.te.disarm()
            return self.handled(event)

        return self.super(self.top)


class Five(async_hsm.Ahsm):
    @async_hsm.state
    def _initial(self, event):
        print("Five _initial")
        self.te = async_hsm.TimeEvent("TICK5")
        return self.tran(self._running)

    @async_hsm.state
    def _running(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("five enter")
            self.te.postEvery(self, 5)
            return self.handled(event)

        elif sig == async_hsm.Signal.TICK5:
            print("five tick")
            return self.handled(event)

        elif sig == async_hsm.Signal.EXIT:
            print("five exit")
            self.te.disarm()
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    # Uncomment this line to get a visual execution trace (to demonstrate debugging)
    # from async_hsm.SimpleSpy import SimpleSpy
    # async_hsm.Spy.enable_spy(SimpleSpy)

    three = Three()
    five = Five()

    three.start(3)
    five.start(5)

    async_hsm.run_forever()
