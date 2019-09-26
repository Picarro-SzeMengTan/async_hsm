#!/usr/bin/env python3
import asyncio
import traceback

import aiohttp_cors
import click
from aiohttp import web
from aiohttp.web import middleware, HTTPInternalServerError
from aiohttp_swagger import setup_swagger

from async_hsm import Ahsm, Event, Framework, Signal, TimeEvent, state

# import logging

# stdio_handler = logging.StreamHandler()
# stdio_handler.setLevel(logging.INFO)
# _logger = logging.getLogger('aiohttp')
# _logger.addHandler(stdio_handler)
# _logger.setLevel(logging.DEBUG)


class SampleService:
    def __init__(self):
        self.app = web.Application(middlewares=[self.my_middleware])
        self.app.router.add_route("GET", "/api1", self.api1)
        self.app.router.add_route("GET", "/api2", self.api2)
        self.app.on_startup.append(self.on_startup)
        self.app.on_shutdown.append(self.on_shutdown)
        self.publish_errors = True

    @middleware
    async def my_middleware(self, request, handler):
        try:
            resp = await handler(request)
        except Exception as e:
            if self.publish_errors:
                Framework.publish(
                    Event(Signal.ERROR, {
                        "exc": e,
                        "traceback": traceback.format_exc(),
                        "location": self.__class__.__name__,
                        "request": request.url
                    }))
            raise HTTPInternalServerError(text=f"Error handling request {request.path_qs}\n{traceback.format_exc()}")
        return resp

    async def on_startup(self, app):
        print("SampleService server is starting up")

    async def on_shutdown(self, app):
        print("SampleService server is shutting down")

    async def api1(self, request):
        """
        ---
        description: Sample API method 1

        tags:
            -   simple
        summary: Sample API method 1
        produces:
            -   application/json
        responses:
            "200":
                description: successful operation.
        """
        1 / 0
        return web.json_response({"message": f"Hello from simple method api1 where data is {request.app['hsm_pool']}"})

    async def api2(self, request):
        """
        ---
        description: Sample API method 2

        tags:
            -   simple
        summary: Sample API method 2
        produces:
            -   application/json
        responses:
            "200":
                description: successful operation.
        """
        return web.json_response({"message": f"Hello from simple method api2 where data is {request.app['hsm_pool']}"})


class MultiServer:
    def __init__(self):
        self.tasks = []
        self.app = None
        self.runner = None
        self.port = None
        self.addr = None
        self.terminate_event = asyncio.Event()

    def set_host(self, port, addr='0.0.0.0'):
        self.port = port
        self.addr = addr

    async def on_startup(self, app):
        await app['hsm_pool'].startup()

    async def on_shutdown(self, app):
        for task in self.tasks:
            task.cancel()
        await app['hsm_pool'].shutdown()

    async def on_cleanup(self, app):
        print("MultiServer is cleaning up")
        self.terminate_event.set()

    async def server_init(self):
        self.app = web.Application()
        self.app.on_startup.append(self.on_startup)
        self.app.on_shutdown.append(self.on_shutdown)
        self.app.on_cleanup.append(self.on_cleanup)
        hsm_pool = HsmPool()
        self.app['hsm_pool'] = hsm_pool

        cors = aiohttp_cors.setup(
            self.app, defaults={"*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )})

        sample_service = SampleService()
        sample_service.app['hsm_pool'] = self.app['hsm_pool']
        self.app.add_subapp("/sample/", sample_service.app)

        setup_swagger(self.app)

        for route in self.app.router.routes():
            cors.add(route)

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.addr, self.port)
        await site.start()
        print(f"======== Running on http://{site._host}:{site._port} ========")

    def handle_exception(self, loop, context):
        msg = context.get("exception", context["message"])
        print(f"Uncaught exception:\n{msg}\n{traceback.format_exc()}")


class MyHsm(Ahsm):
    def __init__(self, parent, name, period):
        super().__init__()
        self.parent = parent
        self.name = name
        self.period = period
        self.count = 0

    async def async_task_example(self, name):
        await asyncio.sleep(1.0)
        # raise ValueError("Error in coroutine")
        print(f"After async_task in {name}")

    @state
    def _initial(self, e):
        Framework.subscribe("ERROR", self)
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
            # raise ValueError("Error raised in notify")
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
            return self.handled(event)
            # if self.name == "alpha":
            #     return self.tran(self._running)
            # else:
            #     return self.tran(self._error)

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


async def asyn_main(host, port):
    service = MultiServer()
    asyncio.get_running_loop().set_exception_handler(service.handle_exception)
    service.set_host(port, addr=host)
    await service.server_init()
    await Framework.done()
    print("After AHSM Framework closed")
    await service.runner.cleanup()
    await service.terminate_event.wait()


@click.command()
@click.option('--host', '-h', default='0.0.0.0', help='Listen address for HTTP server')
@click.option('--port', '-p', default=8002, help='Port for HTTP server')
def main(host, port):
    asyncio.run(asyn_main(host, port))


if __name__ == "__main__":
    main()
