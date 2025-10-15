from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from asyncio import sleep as asleep
from time import time
import aiohttp

from config import DANBOORU_USERNAME, DANBOORU_API_KEY
from bot import bot
from bot.errors import BotException, BotValueError, BotNotFoundError

if TYPE_CHECKING:
    from bot import SlashCommandInteraction, SlashAutocompleteInteraction


logger = getLogger(__name__)
URL_GET_POST = f"https://{DANBOORU_USERNAME}:{DANBOORU_API_KEY}@danbooru.donmai.us/posts.json?&random=true&limit=1"
URL_GET_TAGS = f"https://{DANBOORU_USERNAME}:{DANBOORU_API_KEY}@danbooru.donmai.us/tags.json?&limit=20&search[order]=count&search[name_matches]="


class ApiCache:

    MAX_ENTRIES = 100
    EXPIRE_AFTER = 300  # how long it takes for a cached entry to expire
    FETCH_DELAY = 1.0  # make sure one second is passed between requests

    def __init__(self):
        # Cached data for booru API as {route: [data, expires_at]}.
        # This is used for tag autocompletion and
        # to throttle requests to the API requirement (1 per second for free acc).
        self.d: dict[str, tuple[dict, float | int]] = dict()
        self.last_fetch = 0

    async def get_or_fetch(self, route: str):
        """ get or fetch route and update cache """
        if (r := self.d.get(route)) is not None:
            if r[1] < time():
                logger.debug(f'Using cached response for {route}.')
                return r[0]

        if self.d.__len__() >= self.MAX_ENTRIES:
            self.d.clear()

        r = await self.fetch(route)
        self.d[route] = (r, time())
        return r

    async def fetch(self, route: str, timeout: int = 3) -> dict:
        """ only fetch, do not store result """
        if time() - self.last_fetch < self.FETCH_DELAY:
            await asleep(self.FETCH_DELAY - (time() - self.last_fetch))

        self.last_fetch = time()
        async with aiohttp.ClientSession() as session:
            async with session.get(route, timeout=timeout) as resp:
                return await resp.json()


booru_cache = ApiCache()


@bot.slash_command('anime', expensive=True)
async def show_anime(sci: SlashCommandInteraction, tags: str = None):
    tags = (tags or '').split()
    if len(tags) > 1:
        raise BotValueError('Too many tags.')
    tag_string = '&tags=' + '+'.join(('rating:safe', *tags))

    posts = await booru_cache.fetch(URL_GET_POST + tag_string)

    if type(posts) == dict:
        logger.warning(f'Bad response from API: {posts}')
        raise BotException(f'Request failed, bad API response.')

    if len(posts) == 0:
        raise BotNotFoundError("Nobody here but us chickens!")

    post = posts[0]
    tags = []
    if post['tag_string_character'] != '':
        tags.append("**{0}**: `{1}`".format('characters', post['tag_string_character']))
    if post['tag_string_copyright'] != '':
        tags.append("**{0}**: `{1}`".format('copyright', post['tag_string_copyright']))
    if post['tag_string_artist'] != '':
        tags.append("**{0}**: `{1}`".format('artist', post['tag_string_artist']))

    await sci.reply_raw(embeds=[{
        "title": f"{post['id']}",
        "url": f"https://danbooru.donmai.us/posts/{post['id']}",
        "image": {"url": post['large_file_url']},
        "description": "\n".join(tags)
    }])


@bot.slash_autocomplete('tags')
async def autocomplete_tags(sai: SlashAutocompleteInteraction) -> list[dict]:
    tag_split = sai.value.rsplit(maxsplit=1)
    if len(tag_split) == 2:
        prefix, value = tag_split[0] + ' ', tag_split[1]
    else:
        prefix, value = '', sai.value

    data = await booru_cache.get_or_fetch(URL_GET_TAGS+value+'*')
    return [
        {'name': prefix+i['name'], 'value': prefix+i['name']}
        for i in data
    ][:25]
