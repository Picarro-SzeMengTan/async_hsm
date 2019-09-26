from async_hsm import Ahsm, Event, Signal, Spy, state
from async_hsm.SimpleSpy import SimpleSpy



class HsmExample1(Ahsm):
    @state
    def _initial(self, event):
        Signal.register("E1")
        Signal.register("E2")
        return self.tran(self.state1)

    @state
    def state1(self, e):
        sig = e.signal
        if sig == Signal.ENTRY:
            print("ENTRY action 1")
            return self.handled(e)
        elif sig == Signal.EXIT:
            print("EXIT action 1")
            return self.handled(e)
        elif sig == Signal.INIT:
            print("INIT action 1")
            return self.tran(self.state2)
        elif sig == Signal.E1:
            print("Event 1 action 1")
            return self.handled(event)
        elif sig == Signal.E2:
            print("Event 2 action 1")
            return self.tran(self.state1)
        return self.super(self.top)

    @state
    def state2(self, e):
        sig = e.signal
        if sig == Signal.ENTRY:
            print("ENTRY action 2")
            return self.handled(e)
        elif sig == Signal.EXIT:
            print("EXIT action 2")
            return self.handled(e)
        elif sig == Signal.E1:
            print("Event 1 action 2")
            return self.tran(self.state1)
        elif sig == Signal.E2:
            print("Event 2 action 2")
            return self.tran(self.state3)
        return self.super(self.state1)

    @state
    def state3(self, e):
        sig = e.signal
        if sig == Signal.ENTRY:
            print("ENTRY action 3")
            return self.handled(e)
        elif sig == Signal.EXIT:
            print("EXIT action 3")
            return self.handled(e)
        return self.super(self.state1)


if __name__ == "__main__":
    import signal

    def intrup(*a):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, intrup)
    hsm = HsmExample1()
    Spy.enable_spy(SimpleSpy)
    SimpleSpy.on_framework_add(hsm)
    hsm.init()
    while True:
        sig_name = input('\tEvent --> ')
        try:
            sig = getattr(Signal, sig_name)
        except LookupError:
            print("\nInvalid signal name", end="")
            continue
        event = Event(sig, None)
        hsm.dispatch(event)
