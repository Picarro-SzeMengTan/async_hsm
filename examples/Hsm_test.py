#!/usr/bin/env python3

import asyncio

from async_hsm import Ahsm, Event, Framework, Signal, Spy, state
from async_hsm.SimpleSpy import SimpleSpy


class HsmTest(Ahsm):
    def __init__(self):
        super().__init__()
        # Define signals that this chart subscribes to
        self.foo = None

    @state
    def _initial(self, event):
        Signal.register("a")
        Signal.register("b")
        Signal.register("c")
        Signal.register("d")
        Signal.register("e")
        Signal.register("f")
        Signal.register("g")
        Signal.register("h")
        Signal.register("i")
        Signal.register("t")
        self.foo = 0
        # print(f"foo={self.foo}")
        return self.tran(self._s2)

    @state
    def _s(self, event):
        sig = event.signal
        if sig == Signal.INIT:
            return self.tran(self._s11)
        elif sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.i:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.handled(event)
        elif sig == Signal.e:
            return self.tran(self._s11)
        elif sig == Signal.t:
            return self.tran(self._exit)
        return self.super(self.top)

    @state
    def _s1(self, event):
        sig = event.signal
        if sig == Signal.INIT:
            return self.tran(self._s11)
        elif sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.a:
            return self.tran(self._s1)
        elif sig == Signal.b:
            return self.tran(self._s11)
        elif sig == Signal.c:
            return self.tran(self._s2)
        elif sig == Signal.d:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.tran(self._s)
        elif sig == Signal.f:
            return self.tran(self._s211)
        elif sig == Signal.i:
            return self.handled(event)
        return self.super(self._s)

    @state
    def _s11(self, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.d:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.tran(self._s1)
        elif sig == Signal.g:
            return self.tran(self._s211)
        elif sig == Signal.h:
            return self.tran(self._s)
        return self.super(self._s1)

    @state
    def _s2(self, event):
        sig = event.signal
        if sig == Signal.INIT:
            return self.tran(self._s211)
        elif sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.c:
            return self.tran(self._s1)
        elif sig == Signal.f:
            return self.tran(self._s11)
        elif sig == Signal.i:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.handled(event)
        return self.super(self._s)

    @state
    def _s21(self, event):
        sig = event.signal
        if sig == Signal.INIT:
            return self.tran(self._s211)
        elif sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.a:
            return self.tran(self._s21)
        elif sig == Signal.b:
            return self.tran(self._s211)
        elif sig == Signal.g:
            return self.tran(self._s1)
        return self.super(self._s2)

    @state
    def _s211(self, event):
        sig = event.signal
        if sig == Signal.ENTRY:
            return self.handled(event)
        elif sig == Signal.EXIT:
            return self.handled(event)
        elif sig == Signal.d:
            return self.tran(self._s21)
        elif sig == Signal.h:
            return self.tran(self._s)
        return self.super(self._s21)


async def main():
    import signal
    Spy.enable_spy(SimpleSpy)
    s1 = HsmTest()
    SimpleSpy.on_framework_add(s1)
    interactive = False
    if interactive:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        s1.init()
        while not s1.terminated:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = Event(sig, None)
            s1.dispatch(event)

        print("\nTerminated")
    else:
        seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        # seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        s1.start(0)
        for sig in seq:
            event = Event(getattr(Signal, sig), None)
            s1.postFIFO(event)
        await Framework.done()


if __name__ == "__main__":
    asyncio.run(main())
