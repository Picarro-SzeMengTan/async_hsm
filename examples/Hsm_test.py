#!/usr/bin/env python3


import farc
from farc.SimpleSpy import SimpleSpy as Spy


class HsmTest(farc.Ahsm):
    def __init__(self):
        super().__init__()
        # Define signals that this chart subscribes to
        self.foo = None
        self.running = None

    @farc.state
    def _initial(self, event):
        farc.Signal.register("a")
        farc.Signal.register("b")
        farc.Signal.register("c")
        farc.Signal.register("d")
        farc.Signal.register("e")
        farc.Signal.register("f")
        farc.Signal.register("g")
        farc.Signal.register("h")
        farc.Signal.register("i")
        farc.Signal.register("t")
        self.running = True
        self.foo = 0
        # print(f"foo={self.foo}")
        return self.tran(self._s2)

    @farc.state
    def _s(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(self._s11)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.i:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.handled(event)
        elif sig == farc.Signal.e:
            return self.tran(self._s11)
        elif sig == farc.Signal.t:
            return self.tran(self._exiting)
        return self.super(self.top)

    @farc.state
    def _s1(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(self._s11)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.a:
            return self.tran(self._s1)
        elif sig == farc.Signal.b:
            return self.tran(self._s11)
        elif sig == farc.Signal.c:
            return self.tran(self._s2)
        elif sig == farc.Signal.d:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.tran(self._s)
        elif sig == farc.Signal.f:
            return self.tran(self._s211)
        elif sig == farc.Signal.i:
            return self.handled(event)
        return self.super(self._s)

    @farc.state
    def _s11(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.d:
            if self.foo:
                self.foo = 0
                # print(f"foo={self.foo}")
                return self.tran(self._s1)
        elif sig == farc.Signal.g:
            return self.tran(self._s211)
        elif sig == farc.Signal.h:
            return self.tran(self._s)
        return self.super(self._s1)

    @farc.state
    def _s2(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(self._s211)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.c:
            return self.tran(self._s1)
        elif sig == farc.Signal.f:
            return self.tran(self._s11)
        elif sig == farc.Signal.i:
            if not self.foo:
                self.foo = 1
                # print(f"foo={self.foo}")
                return self.handled(event)
        return self.super(self._s)

    @farc.state
    def _s21(self, event):
        sig = event.signal
        if sig == farc.Signal.INIT:
            return self.tran(self._s211)
        elif sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.a:
            return self.tran(self._s21)
        elif sig == farc.Signal.b:
            return self.tran(self._s211)
        elif sig == farc.Signal.g:
            return self.tran(self._s1)
        return self.super(self._s2)

    @farc.state
    def _s211(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)
        elif sig == farc.Signal.d:
            return self.tran(self._s21)
        elif sig == farc.Signal.h:
            return self.tran(self._s)
        return self.super(self._s21)

    @farc.state
    def _exiting(self, event):
        sig = event.signal
        if sig == farc.Signal.ENTRY:
            self.running = False
            farc.Framework.stop()
            return self.handled(event)
        elif sig == farc.Signal.EXIT:
            return self.handled(event)

        return self.super(self.top)


if __name__ == "__main__":
    farc.Spy.enable_spy(Spy)
    s1 = HsmTest()
    Spy.on_framework_add(s1)
    interactive = True
    if interactive:
        s1.init()
        while s1.running:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(farc.Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = farc.Event(sig, None)
            s1.dispatch(event)

        print("\nTerminated")
    else:
        # seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        s1.start(0)
        for sig in seq:
            event = farc.Event(getattr(farc.Signal, sig), None)
            s1.postFIFO(event)
        farc.run_forever()
