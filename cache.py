from time import time
from asyncio import sleep as asleep
from logging import getLogger
from typing import Callable

logger = getLogger(__name__)


class ApiCache:
    MAX_ENTRIES = 100
    EXPIRE_AFTER = 300  # how long it takes for a cached entry to expire
    FETCH_DELAY = 1.0  # make sure one second is passed between requests

    def __init__(self, fetch_f: Callable):
        # Cached data for booru API as {route: [data, expires_at]}.
        # This is used for tag autocompletion and
        # to throttle requests to the API requirement (1 per second for free acc).
        self.fetch_f = fetch_f
        self.d: dict[str, tuple[dict, float | int]] = dict()
        self.last_fetch = 0

    async def get_or_fetch(self, route: str, *args, **kwargs):
        """ get or fetch route and update cache """
        if (r := self.d.get(route)) is not None:
            if r[1] < time():
                logger.debug(f'Using cached response for {route}.')
                return r[0]

        if self.d.__len__() >= self.MAX_ENTRIES:
            self.d.clear()

        r = await self.fetch_f(route, *args, **kwargs)
        self.d[route] = (r, time())
        return r

    async def fetch(self, route: str, *args, **kwargs) -> dict:
        """ only fetch, do not store result """
        if time() - self.last_fetch < self.FETCH_DELAY:
            await asleep(self.FETCH_DELAY - (time() - self.last_fetch))

        self.last_fetch = time()
        return await self.fetch_f(route, *args, **kwargs)
