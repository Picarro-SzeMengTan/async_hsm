#!/usr/bin/env python3

"""UDP Relay AHSM for async_hsm
This is a demonstration program that
relays UDP messages to/from the async_hsm framework.

This file represents the "server" which listens for a connection.
A client such as netcat (nc) can be used to issue UDP datagrams
to the server.
When a client is present, the server starts a timer
to periodically echo back the most recently received message.
When the client is gone, the server awaits the next datagram.

References:
- https://www.pythonsheets.com/notes/python-asyncio.html
- https://docs.python.org/3.4/library/asyncio.html
"""

import asyncio

import async_hsm


UDP_PORT = 4242


class UdpServer:
    def connection_made(self, transport):
        pass

    def datagram_received(self, data, addr):
        self.on_datagram(data, addr)

    def error_received(self, error):
        self.on_error(error)


class UdpRelayAhsm(async_hsm.Ahsm):

    @async_hsm.state
    def _initial(self, event):
        async_hsm.Framework.subscribe("NET_ERR", self)
        async_hsm.Framework.subscribe("NET_RXD", self)
        self.tmr = async_hsm.TimeEvent("FIVE_COUNT")

        loop = asyncio.get_event_loop()
        server = loop.create_datagram_endpoint(UdpServer, local_addr=("localhost", UDP_PORT))
        self.transport, self.protocol = loop.run_until_complete(server)
        return self.tran(self._waiting)


    @async_hsm.state
    def _waiting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("Awaiting a UDP datagram on port {0}.  Try: $ nc -u localhost {0}".format(UDP_PORT))
            return self.handled(event)

        elif sig == async_hsm.Signal.NET_RXD:
            self.latest_msg, self.latest_addr = event.value
            print("RelayFrom(%s): %r" % (self.latest_addr, self.latest_msg.decode()))
            return self.tran(self._relaying)

        elif sig == async_hsm.Signal.SIGTERM:
            return self.tran(self._exiting)

        return self.super(self.top)


    @async_hsm.state
    def _relaying(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            self.tmr.postEvery(self, 5.000)
            return self.handled(event)

        elif sig == async_hsm.Signal.NET_RXD:
            self.latest_msg, self.latest_addr = event.value
            print("RelayFrom(%s): %r" % (self.latest_addr, self.latest_msg.decode()))
            return self.handled(event)

        elif sig == async_hsm.Signal.FIVE_COUNT:
            s = "Latest: %r\n" % self.latest_msg.decode()
            self.transport.sendto(s.encode(), self.latest_addr)
            return self.handled(event)

        elif sig == async_hsm.Signal.NET_ERR:
            return self.tran(self._waiting)

        elif sig == async_hsm.Signal.SIGTERM:
            self.tmr.disarm()
            return self.tran(self._exiting)

        elif sig == async_hsm.Signal.EXIT:
            print("Leaving timer event running so Ctrl+C will be handled on Windows")
            return self.handled(event)

        return self.super(self.top)


    @async_hsm.state
    def _exiting(self, event):
        sig = event.signal
        if sig == async_hsm.Signal.ENTRY:
            print("exiting")
            self.transport.close()
            return self.handled(event)
        return self.super(self.top)


    # Callbacks interact via messaging
    @staticmethod
    def on_datagram(data, addr):
        e = async_hsm.Event(async_hsm.Signal.NET_RXD, (data,addr))
        async_hsm.Framework.publish(e)

    @staticmethod
    def on_error(error):
        e = async_hsm.Event(async_hsm.Signal.NET_ERR, (error))
        async_hsm.Framework.publish(e)


if __name__ == "__main__":
    from async_hsm.SimpleSpy import SimpleSpy
    async_hsm.Spy.enable_spy(SimpleSpy)
    relay = UdpRelayAhsm()
    relay.start(0)

    async_hsm.run_forever()
