from __future__ import annotations

import logging
from time import time
from typing import cast, TYPE_CHECKING
from logging import getLogger
from nextcore.gateway import ShardManager
from nextcore.http import BotAuthentication, HTTPClient, Route, HTTPRequestStatusError

from config import DC_BOT_TOKEN, DC_BOT_INTENTS, DC_SHARD_ID, DC_SHARD_COUNT
from .events import BotEvents
from bot.interactions import SlashCommandCallback

if TYPE_CHECKING:
    from typing import Literal, Callable, Coroutine
    from nextcore.gateway import Shard
    from bot import Guild

logger = getLogger(__name__)


class ApiCache:

    MAX_ENTRIES = 100

    def __init__(self):
        # cached data for self.api_get_cached as {route: [data, expires_at]}
        # this is used in case of slash commands autocomplete and such
        self.d: dict[str, tuple[dict, float | int]] = dict()

    def get(self, route: str) -> dict | None:
        if (cached := self.d.get(route)) is not None:
            if time() < cached[1]:
                logger.debug(f'Using cached response for {route}.')
                return cached[0]

    def set(self, route: str, data: dict, expires_at: float | int):
        if self.d.__len__() >= self.MAX_ENTRIES:
            self.d.clear()
        self.d[route] = (data, expires_at)


class BotShardManager(ShardManager):
    """ Adds shard_disconnect event to ShardManager """

    async def _on_shard_disconnect(self, code: int | bool):
        await self.event_dispatcher.dispatch('shard_disconnect', code)

    def _spawn_shard(self, shard_id: int, shard_count: int) -> Shard:
        shard = super()._spawn_shard(shard_id, shard_count)
        shard.dispatcher.add_listener(self._on_shard_disconnect, 'disconnect')
        shard.dispatcher.add_listener(self._on_shard_disconnect, 'client_disconnect')
        return shard


class Bot:

    def __init__(self):
        self.token = DC_BOT_TOKEN
        self.auth = BotAuthentication(self.token)
        self.ready = False  # if the bot is fully ready to operate
        self.first_ready = True  # if the bot is ready for first time or reconnected
        self.running = True
        self.unavailable_guilds: list[str] = []
        self.cache = ApiCache()
        self._on_close_tasks = []
        self._on_think_tasks = []

        self.http_client = HTTPClient()
        self.shard_manager = BotShardManager(
            self.auth, DC_BOT_INTENTS, self.http_client, shard_count=DC_SHARD_COUNT, shard_ids=[DC_SHARD_ID]
        )
        self.event_dispatcher = self.shard_manager.event_dispatcher
        self.slash_commands: dict[str, SlashCommandCallback] = dict()
        self.slash_autocompletes: dict[str, Callable] = dict()
        self.guilds: dict[str, Guild] = {}

        self.events = BotEvents(self)

    async def serve(self):
        await self.http_client.setup()

        # This should return once all shards have started to connect.
        # This does not mean they are connected.
        await self.shard_manager.connect()

        # Raise an error and exit whenever a critical error occurs
        (error,) = await self.shard_manager.dispatcher.wait_for(lambda: True, "critical")

        raise cast(Exception, error)

    def slash_command(self, cmd_name: str, ephemeral: bool = False, expensive: bool = False):
        """ Decorator to register a slash command """
        def _decorator(callback: Callable):
            logger.info(f'Registered slash command /{cmd_name} - {callback.__name__}.')
            self.slash_commands[cmd_name] = SlashCommandCallback(callback, ephemeral=ephemeral, expensive=expensive)
        return _decorator

    def on_think(self, callback: Callable):
        """ Decorator to register an on_think task """
        logger.info(f'Registered on think task - {callback.__name__}.')
        self._on_think_tasks.append(callback)

    def slash_autocomplete(self, option_name: str):
        """ Decorator to register a slash command option autocomplete """
        def _decorator(callback: Callable):
            logger.info(f'Registered slash option autocomplete {option_name} - {callback.__name__}.')
            self.slash_autocompletes[option_name] = callback
        return _decorator

    def on_close(self):
        """ Decorator to register a task on bot exit """
        def _decorator(callback: Callable):
            self._on_close_tasks.append(callback)
        return _decorator

    async def think(self, frame_time: float):
        if self.ready:
            for task in self._on_think_tasks:
                await task(frame_time)

    @staticmethod
    async def quiet(coro: Coroutine):
        """ Run a request ignoring status errors (Forbidden, NotFound, etc) """
        try:
            return coro
        except HTTPRequestStatusError:
            pass

    async def api_get(self, route: str) -> dict:
        """ Do api GET and return json response """

        route = Route('GET', route)
        resp = await self.http_client.request(
            route,
            rate_limit_key=self.auth.rate_limit_key,
            headers=self.auth.headers
        )
        return await resp.json()

    async def api_get_cached(self, route: str, expire_delay: int | float = 15) -> dict:
        """ same as api_get but with simple route caching """
        if (data := self.cache.get(route)) is not None:
            return data
        data = await self.api_get(route)
        self.cache.set(route, data, time()+expire_delay)
        return data

    async def api_post(self, route: str, data: dict, method: Literal['POST', 'PATCH'] = 'POST') -> dict:
        """ Do api POST and return json response """
        route = Route(method, route)
        resp = await self.http_client.request(
            route,
            rate_limit_key=self.auth.rate_limit_key,
            json=data,
            headers=self.auth.headers
        )
        return await resp.json()

    async def api_put(self, route: str, data: dict) -> int:
        """ Do api POST and return json response """
        route = Route('PUT', route)
        resp = await self.http_client.request(
            route,
            rate_limit_key=self.auth.rate_limit_key,
            json=data,
            headers=self.auth.headers
        )
        return resp.status

    async def api_delete(self, route: str) -> int:
        """ Do api DELETE and return json response """
        route = Route('DELETE', route)
        resp = await self.http_client.request(
            route,
            rate_limit_key=self.auth.rate_limit_key,
            headers=self.auth.headers
        )
        return resp.status

    async def close(self):
        for task in self._on_close_tasks:
            await task()
        await self.shard_manager.close()
