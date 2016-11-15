import asyncio
import logging
import threading

from server.net import connect_client

log = logging.getLogger(__name__)


class NetThread(threading.Thread):

    def __init__(self, world, *args, **kw):
        super().__init__(*args, **kw)
        self._world = world
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self._main_task = self.loop.create_task(self.main_coroutine())

    # Thread interface methods

    def run(self):
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        else:
            if not self._main_task.done():
                self._main_task.cancel()
            self.loop.run_until_complete(self._main_task)
            self.loop.close()

    def stop(self):
        if self.is_alive():
            self.loop.call_soon_threadsafe(self.loop.stop)

    # Asyncio task

    async def main_coroutine(self):
        try:
            _, self.conn = await connect_client(
                0,
                "127.0.0.1",
                9999,
                loop=self.loop)
        except asyncio.CancelledError:
            pass
        except Exception:
            log.exception("Unexpected network error")
