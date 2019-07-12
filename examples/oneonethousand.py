#!/usr/bin/env python3


import asyncio

import async_hsm


class Mississippi(async_hsm.Ahsm):

    @async_hsm.state
    def _initial(self, event):
        print("_initial")
        self.teCount = async_hsm.TimeEvent("COUNT")
        self.tePrint = async_hsm.TimeEvent("PRINT")
        return self.tran(self._counting)


    @async_hsm.state
    def _counting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_counting enter")
            self._count = 0
            self.teCount.postEvery(self, 0.001)
            self.tePrint.postEvery(self, 1.000)
            return self.handled(event)

        elif sig == async_hsm.Signal.COUNT:
            self._count += 1
            return self.handled(event)

        elif sig == async_hsm.Signal.PRINT:
            print(self._count, "millis")
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    print("Check to see how much CPU% a simple 1ms periodic function uses.")
    ms = Mississippi()
    ms.start(0)

    async_hsm.run_forever()
