#!/usr/bin/env python3
import asyncio
import traceback

from async_hsm import Ahsm, Event, Framework, Signal, Spy, TimeEvent, state


class MyHsm(Ahsm):
    def __init__(self, parent, name, period):
        super().__init__()
        self.parent = parent
        self.name = name
        self.period = period
        self.count = 0
        self.publish_errors = False

    async def async_task_example(self, name):
        await asyncio.sleep(1.0)
        raise ValueError("Error in coroutine")
        print(f"After async_task in {name}")

    @state
    def _initial(self, e):
        Framework.subscribe("NOTIFY", self)
        Framework.subscribe("TERMINATE", self)
        self.te = TimeEvent(f"TIMER_{self.name}")
        return self.tran(self._running)

    @state
    def _running(self, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print(f"{self.name} enters running state, period {self.period}")
            self.te.postEvery(self, self.period)
            # raise ValueError("Exception in entry handler for _running")
            return self.handled(event)

        elif sig == getattr(Signal, f"TIMER_{self.name}"):
            self.count += 1
            print(f"{self.name} receives tick")
            self.postFIFO(Event(Signal.NOTIFY, f"{self.__class__.__name__}: {self.name}"))
            raise ValueError("Error raised in notify")
            return self.handled(event)

        elif sig == Signal.NOTIFY:
            print(f"Received Signal.NOTIFY with payload {event.value}")
            self.run_async(self.async_task_example(self.name))
            return self.handled(event)

        elif sig == Signal.TERMINATE:
            print("Received TERMINATE")
            return self.tran(self._exit)

        elif sig == Signal.EXIT:
            self.te.disarm()
            return self.handled(event)

        elif sig == Signal.ERROR:
            print(f"ERROR: {event.value}")
            if self.name == "alpha":
                return self.tran(self._running)
            else:
                return self.tran(self._error)

        return self.super(self.top)

    @state
    def _error(self, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            print(f"{self.name} in error state")
            self.postFIFO(Event(Signal.TERMINATE, None))
            return self.handled(event)
        return self.super(self._running)


class HsmPool:
    """
    Start a collection of HSMs running in a single asyncio event loop.
    We wish to investigate exception handling and error recovery so that
    the HSM in which an exception occurs is identified and so that an
    error in one does not cause all machines to be killed
    """
    def __init__(self):
        self.hsm1 = MyHsm(self, 'alpha', 3)
        self.hsm2 = MyHsm(self, 'beta', 5)
        self.tasks = []

    async def shutdown(self):
        print(f"Calling shutdown in HsmPool")
        for task in self.tasks:
            task.cancel()

    async def startup(self):
        try:
            print(f"Starting up multiple state machines")
            self.hsm1.start(1)
            self.hsm2.start(2)
        except Exception:
            print(f"Error setting up state machines\n{traceback.format_exc()}")
            raise


async def main():
    # import async_hsm
    # from async_hsm.SimpleSpy import SimpleSpy
    # async_hsm.Spy.enable_spy(SimpleSpy)
    try:
        multi = HsmPool()
        await multi.startup()
        await Framework.done()
    except Exception:
        print(f"\nCaught exception in main\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
