#!/usr/bin/env python3

"""
Copyright 2018 Dean Hall.  See LICENSE for details.

dpp.py - the Dining Philosopher's Problem
         implementation translated from Chaper 9.2 of PSiCC
         [https://newcontinuum.dl.sourceforge.net/project/qpc/doc/PSiCC2.pdf]
"""

import asyncio
import random

import async_hsm


N_PHILO = 10

async_hsm.Signal.register("EAT")
async_hsm.Signal.register("DONE")
async_hsm.Signal.register("TERMINATE")
async_hsm.Signal.register("HUNGRY")

def PHILO_ID(act):
    global philo
    return philo.index(act)

def RIGHT(n):
    return (n + N_PHILO - 1) % N_PHILO

def LEFT(n):
    return (n + 1) % N_PHILO

def THINK_TIME():
    return random.randrange(1, 9)

def EAT_TIME():
    return random.randrange(1, 9)

class Table(async_hsm.Ahsm):
    def __init__(self,):
        super().__init__()
        self.fork = ["FREE",] * N_PHILO
        self.isHungry = [False,] * N_PHILO

    @async_hsm.state
    def _initial(self, event):
        async_hsm.Framework.subscribe("DONE", self)
        async_hsm.Framework.subscribe("TERMINATE", self)
        return self.tran(self._serving)

    @async_hsm.state
    def _serving(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.HUNGRY:
            # BSP.busyDelay()
            n = event.value
            assert n < N_PHILO and not self.isHungry[n]
            print(n, "hungry")
            m = LEFT(n)
            if self.fork[m] == "FREE" and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                e = async_hsm.Event(async_hsm.Signal.EAT, n)
                async_hsm.Framework.publish(e)
                print(n, "eating")
            else:
                self.isHungry[n] = True
            return self.handled(event)

        elif sig == async_hsm.Signal.DONE:
            # BSP.busyDelay()
            n = event.value
            assert n < N_PHILO and not self.isHungry[n]
            print(n, "thinking")
            m = LEFT(n)
            assert self.fork[n] == "USED" and self.fork[m] == "USED"
            self.fork[m] = "FREE"
            self.fork[n] = "FREE"
            m = RIGHT(n)
            if self.isHungry[m] and self.fork[m] == "FREE":
                self.fork[n] = "USED"
                self.fork[m] = "USED"
                self.isHungry[m] = False
                e = async_hsm.Event(async_hsm.Signal.EAT, m)
                async_hsm.Framework.publish(e)
                print(m, "eating")
            m = LEFT(n)
            n = LEFT(m)
            if self.isHungry[m] and self.fork[n] == "FREE":
                self.fork[m] = "USED"
                self.fork[n] = "USED"
                self.isHungry[m] = False
                e = async_hsm.Event(async_hsm.Signal.EAT, m)
                async_hsm.Framework.publish(e)
                print(m, "eating")
            return self.handled(event)

        elif sig == async_hsm.Signal.TERMINATE:
            async_hsm.Framework.stop()

        return self.super(self.top)


class Philo(async_hsm.Ahsm):

    @async_hsm.state
    def _initial(self, event):
        self.timeEvt = async_hsm.TimeEvent("TIMEOUT")
        async_hsm.Framework.subscribe("EAT", self)
        return self.tran(self._thinking)

    @async_hsm.state
    def _thinking(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            self.timeEvt.postIn(self, THINK_TIME())
            status = self.handled(event)

        elif sig == async_hsm.Signal.TIMEOUT:
            status = self.tran(self._hungry)

        elif sig == async_hsm.Signal.EAT or sig == async_hsm.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status

    @async_hsm.state
    def _hungry(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            e = async_hsm.Event(async_hsm.Signal.HUNGRY, PHILO_ID(self))
            async_hsm.Framework.post_by_name(e, "Table")
            status = self.handled(event)

        elif sig == async_hsm.Signal.EAT:
            if event.value == PHILO_ID(self):
                status = self.tran(self._eating)
            else:
                status = self.super(self.top) # UNHANDLED

        elif sig == async_hsm.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status

    @async_hsm.state
    def _eating(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            self.timeEvt.postIn(self, EAT_TIME())
            status = self.handled(event)

        elif sig == async_hsm.Signal.EXIT:
            e = async_hsm.Event(async_hsm.Signal.DONE, PHILO_ID(self))
            async_hsm.Framework.publish(e)
            status = self.handled(event)

        elif sig == async_hsm.Signal.TIMEOUT:
            status = self.tran(self._thinking)

        elif sig == async_hsm.Signal.EAT or sig == async_hsm.Signal.DONE:
            assert event.value != PHILO_ID(self)
            status = self.handled(event)

        else:
            status = self.super(self.top)
        return status


def main():
    global philo

    table = Table()
    table.start(0)

    philo = []
    for n in range(N_PHILO):
        p = Philo()
        p.start(n+1)
        philo.append(p)

    async_hsm.run_forever()


if __name__ == "__main__":
    main()
