#!/usr/bin/env python3


import async_hsm
from async_hsm.SimpleSpy import SimpleSpy as Spy

from async_hsm import Catch, Event, Factory, Framework, HsmDescription, Signal, State
from types import MethodType

class HsmTest(Factory):
    def __init__(self):
        super().__init__()

    def __getattr__(self, attr):
        """Returns a function that transitions to target when
        a method with the name goto_target is encountered"""
        if attr.startswith("goto_"):
            target = attr[len("goto_"):]

            def func(e):
                return self.tran(target)
            return func
        else:
            raise NotImplementedError

    def setup(self):
        self.running = True
        self.foo = 0

    def handle_i_in_s(self, e):
        if self.foo:
            self.foo = 0
            return self.handled(e)

    def handle_d_in_s1(self, e):
        if not self.foo:
            self.foo = 1
            return self.tran("s")

    def handle_d_in_s11(self, e):
        if self.foo:
            self.foo = 0
            return self.tran("s1")

    def handle_i_in_s2(self, e):
        if not self.foo:
            self.foo = 1
            return self.handled(e)
    
    def handle_entry_in_exiting(self, e):
        self.running = False
        async_hsm.Framework.stop()
        return self.handled(e)


hsm = HsmDescription("s2", "setup", ["a", "b", "c", "d", "e", "f", "g", "h", "i", "t"], [
    State("s", None,
        [Catch("INIT", "goto_s11"),
         Catch("i", "handle_i_in_s"),
         Catch("e", "goto_s11"),
         Catch("t", "goto_exiting")]),
    State("s1", "s",
        [Catch("INIT", "goto_s11"),
         Catch("a", "goto_s1"),
         Catch("b", "goto_s11"),
         Catch("c", "goto_s2"),
         Catch("d", "handle_d_in_s1"),
         Catch("f", "goto_s211"),
         Catch("i", "handled")]),
    State("s11", "s1",
        [Catch("d", "handle_d_in_s11"),
         Catch("g", "goto_s211"),
         Catch("h", "goto_s")]),
    State("s2", "s",
        [Catch("INIT", "goto_s211"),
         Catch("c", "goto_s1"),
         Catch("f", "goto_s11"),
         Catch("i", "handle_i_in_s2")]),
    State("s21", "s2",
        [Catch("INIT", "goto_s211"),
         Catch("a", "goto_s21"),
         Catch("b", "goto_s211"),
         Catch("g", "goto_s1")]),
    State("s211", "s21",
        [Catch("d", "goto_s21"),
         Catch("h", "goto_s")]),
    State("exiting", None,
        [Catch("ENTRY", "handle_entry_in_exiting"),
         Catch("h", "goto_s")]),
])

if __name__ == "__main__":
    async_hsm.Spy.enable_spy(Spy)
    HsmTest.build_hsm(hsm)
    machine = HsmTest() 
    Spy.on_framework_add(machine)
    interactive = True
    if interactive:
        machine.init()
        while machine.running:
            sig_name = input('\tEvent --> ')
            try:
                sig = getattr(async_hsm.Signal, sig_name)
            except LookupError:
                print("\nInvalid signal name", end="")
                continue
            event = async_hsm.Event(sig, None)
            machine.dispatch(event)

        print("\nTerminated")
    else:
        # seq = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a', 't']
        seq = ['g', 'i', 'a', 'd', 'd', 'c', 'e', 'e', 'g', 'i', 'i', 't']
        machine.start(0)
        for sig in seq:
            event = async_hsm.Event(getattr(async_hsm.Signal, sig), None)
            machine.postFIFO(event)
        async_hsm.run_forever()
