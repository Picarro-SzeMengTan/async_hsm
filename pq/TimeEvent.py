from .Ahsm import Ahsm
from .Signal import Signal
from .Framework import Framework


class TimeEvent(object):
    """TimeEvent is a composite class that contains an Event.
    A TimeEvent is created by the application and added to the Framework.
    The Framework then emits the event after the given delay.
    A one-shot TimeEvent is created by calling the postIn() method.
    A periodic TimeEvent is created by calling the postEvery() method.
    """
    def __init__(self, signame):
        assert type(signame) == str
        self.signal = Signal.register(signame)
        self.value = None


    def postIn(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = 0
        Framework.addTimeEvent(self, delta)


    def postEvery(self, act, delta):
        """Posts this TimeEvent to the given Ahsm after the time delta
        and every time delta thereafter until disarmed.
        """
        assert issubclass(type(act), Ahsm)
        self.act = act
        self.interval = delta
        Framework.addTimeEvent(self, delta)


    def disarm(self):
        """Removes this TimeEvent from the Framework's active time events.
        """
        self.act = None
        Framework.removeTimeEvent(self)


# Keyboard Events
# at init time, either copy from app6.py or use urwid
