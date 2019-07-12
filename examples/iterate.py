#!/usr/bin/env python3


import asyncio

import async_hsm


class Iterate(async_hsm.Ahsm):
    def __init__(self,):
        super().__init__()
        async_hsm.Signal.register("ITERATE")


    @async_hsm.state
    def _initial(self, event):
        print("_initial")
        self.iter_evt = async_hsm.Event(async_hsm.Signal.ITERATE, None)
        return self.tran(self._iterating)


    @async_hsm.state
    def _iterating(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("_iterating")
            self.count = 10
            self.postFIFO(self.iter_evt)
            return self.handled(event)

        elif sig == async_hsm.Signal.ITERATE:
            print(self.count)

            if self.count == 0:
                return self.tran(self._exiting)
            else:
                # do work
                self.count -= 1
                self.postFIFO(self.iter_evt)
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
    sl = Iterate()
    sl.start(0)

    async_hsm.run_forever()