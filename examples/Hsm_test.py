#!/usr/bin/env python3


import async_hsm
from async_hsm.SimpleSpy import SimpleSpy as Spy


class HsmTest(async_hsm.Ahsm):
    def __init__(self):
        super().__init__()
        # Define signals that this chart subscribes to
        self.foo = None
        self.running = None

    @async_hsm.state
    def _initial(self, event):
        async_hsm.Signal.register("a")
        async_hsm.Signal.register("b")
        async_hsm.Signal.register("c")
        async_hsm.Signal.register("d")
        async_hsm.Signal.register("e")
        async_hsm.Signal.register("f")
        async_hsm.Signal.register("g")
        async_hsm.Signal.register("h")
        async_hsm.Signal.register("i")
        async_hsm.Signal.register("t")
        self.running = True
        self.foo = 0
        # print(f"foo={self.foo}")
        return self.tran(self._s2)

    @async_hsm.state
    def _s(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.INIT:
            return self.tran(self._s11)
        elif sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.i:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.handled(event)
        elif sig == async_hsm.Signal.e:
            return self.tran(self._s11)
        elif sig == async_hsm.Signal.t:
            return self.tran(self._exiting)
        return self.super(self.top)

    @async_hsm.state
    def _s1(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.INIT:
            return self.tran(self._s11)
        elif sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.a:
            return self.tran(self._s1)
        elif sig == async_hsm.Signal.b:
            return self.tran(self._s11)
        elif sig == async_hsm.Signal.c:
            return self.tran(self._s2)
        elif sig == async_hsm.Signal.d:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.tran(self._s)
        elif sig == async_hsm.Signal.f:
            return self.tran(self._s211)
        elif sig == async_hsm.Signal.i:
            return self.handled(event)
        return self.super(self._s)

    @async_hsm.state
    def _s11(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.d:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.tran(self._s1)
        elif sig == async_hsm.Signal.g:
            return self.tran(self._s211)
        elif sig == async_hsm.Signal.h:
            return self.tran(self._s)
        return self.super(self._s1)

    @async_hsm.state
    def _s2(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.INIT:
            return self.tran(self._s211)
        elif sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.c:
            return self.tran(self._s1)
        elif sig == async_hsm.Signal.f:
            return self.tran(self._s11)
        elif sig == async_hsm.Signal.i:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.handled(event)
        return self.super(self._s)

    @async_hsm.state
    def _s21(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.INIT:
            return self.tran(self._s211)
        elif sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.a:
            return self.tran(self._s21)
        elif sig == async_hsm.Signal.b:
            return self.tran(self._s211)
        elif sig == async_hsm.Signal.g:
            return self.tran(self._s1)
        return self.super(self._s2)

    @async_hsm.state
    def _s211(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)
        elif sig == async_hsm.Signal.d:
            return self.tran(self._s21)
        elif sig == async_hsm.Signal.h:
            return self.tran(self._s)
        return self.super(self._s21)

    @async_hsm.state
    def _exiting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            self.running = False
            async_hsm.Framework.stop()
            return self.handled(event)
        elif sig == async_hsm.Signal.EXIT:
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    async_hsm.Spy.enable_spy(Spy)
    s1 = HsmTest()
    Spy.on_framework_add(s1)
    interactive = True
    if interactive:
        s1.init()
        while s1.running:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(async_hsm.Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = async_hsm.Event(sig, None)
            s1.dispatch(event)

        print("\nTerminated")
    else:
        # seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        s1.start(0)
        for sig in seq:
            event = async_hsm.Event(getattr(async_hsm.Signal, sig), None)
            s1.postFIFO(event)
        async_hsm.run_forever()
