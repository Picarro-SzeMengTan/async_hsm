#!/usr/bin/env python3


import asyncio

import async_hsm


class Stoplight(async_hsm.Ahsm):

    @async_hsm.state
    def _initial(self, event):
        print("Stoplight _initial")

        te = async_hsm.TimeEvent("TIME_TICK")
        te.postEvery(self, 2.0)

        return self.tran(self._red)


    @async_hsm.state
    def _red(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_red enter")
            return self.handled(event)

        elif sig == async_hsm.Signal.TIME_TICK:
            print("_red next")
            return self.tran(self._green)

        elif sig == async_hsm.Signal.EXIT:
            print("_red exit")
            return self.handled(event)

        return self.super(self.top)


    @async_hsm.state
    def _green(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_green enter")
            return self.handled(event)

        elif sig == async_hsm.Signal.TIME_TICK:
            print("_green next")
            return self.tran(self._red)

        elif sig == async_hsm.Signal.EXIT:
            print("_green exit")
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    # from async_hsm.SimpleSpy import SimpleSpy
    # async_hsm.Spy.enable_spy(SimpleSpy)
    sl = Stoplight()
    sl.start(0)

    async_hsm.run_forever()
