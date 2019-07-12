#!/usr/bin/env python3


import asyncio
import async_hsm

class Countdown(async_hsm.Ahsm):
    def __init__(self, count=3):
        super().__init__()
        self.count = count


    @async_hsm.state
    def _initial(self, event):
        print("_initial")
        self.te = async_hsm.TimeEvent("TIME_TICK")
        return self.tran(self._counting)


    @async_hsm.state
    def _counting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_counting")
            self.te.postIn(self, 1.0)
            return self.handled(event)

        elif sig == async_hsm.Signal.TIME_TICK:
            print(self.count)

            if self.count == 0:
                return self.tran(self._exiting)
            else:
                self.count -= 1
                self.te.postIn(self, 1.0)
                return self.handled(event)

        return self.super(self.top)


    @async_hsm.state
    def _exiting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_exiting")
            async_hsm.Framework.stop()
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    # from SelectiveSpy import SelectiveSpy as Spy
    # async_hsm.Spy.enable_spy(Spy)
    sl = Countdown(10)
    sl.start(0)

    async_hsm.run_forever()
