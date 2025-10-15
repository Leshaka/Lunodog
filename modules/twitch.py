from __future__ import annotations

from logging import getLogger
from time import time
from nextcore.http.errors import UnauthorizedError, HTTPRequestStatusError
from datetime import datetime, timedelta
import aiohttp
import json
from collections import defaultdict

from db import db
from common import find
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_POLL_DELAY
from bot import bot


logger = getLogger(__name__)
LAST_TWITCH_POLL = time()
TOKEN_URL = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials"
TOKEN = None
STREAMS_URL = "https://api.twitch.tv/helix/streams?first=100&{channels}"
GAMES_URL = "https://api.twitch.tv/helix/games?{ids}"
USERS_URL = "https://api.twitch.tv/helix/users?{ids}"


async def _fetch_twitch_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(TOKEN_URL, raise_for_status=True) as resp:
            d = json.loads(await resp.text())
            return d['access_token']


async def _fetch_twitch_url(url: str) -> dict:
    """ Fetch a twitch API url, return data as dict, refetch TOKEN if necessary"""
    global TOKEN

    async def _fetch() -> dict:
        logger.debug(f'fetching url {url}')
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={'client-id': TWITCH_CLIENT_ID, 'Authorization': 'Bearer ' + TOKEN},
                raise_for_status=True
            ) as r:
                logger.debug(f'status code is {r.status}')
                return (await r.json())['data']

    if not TOKEN:
        TOKEN = await _fetch_twitch_token()

    try:
        return await _fetch()
    except UnauthorizedError:
        TOKEN = await _fetch_twitch_token()
        return await _fetch()


async def _fetch_twitch_streams(*user_names: str) -> list[dict]:
    if not len(user_names):
        return []

    streams = await _fetch_twitch_url(
        STREAMS_URL.format(channels="&".join(('user_login=' + name for name in user_names)))
    )
    logger.warning(streams)
    if not len(streams):
        return []

    game_ids = set((i['game_id'] for i in streams))
    games = await _fetch_twitch_url(
        GAMES_URL.format(ids="&".join(('id=' + game_id for game_id in game_ids)))
    )
    games = {i['id']: i for i in games}

    user_ids = set((i['user_id'] for i in streams))
    users = await _fetch_twitch_url(
        USERS_URL.format(ids="&".join(('id=' + user_id for user_id in user_ids)))
    )
    users = {i['id']: i for i in users}

    return [
        {
            'stream_id': int(stream_data['id']),
            'user_id': int(stream_data['user_id']),
            'user_name': stream_data['user_name'],
            'user_avatar': users.get(stream_data['user_id'])['profile_image_url'],
            'game_name': games.get(stream_data['game_id'])['name'],
            'game_thumbnail': games.get(stream_data['game_id'])['box_art_url'],
            'title': stream_data['title'],
            'started_at': int(datetime.fromisoformat(stream_data['started_at'].rstrip('Z')).timestamp()),
            'ended_at': None,
            'is_live': True,
            'thumbnail': stream_data['thumbnail_url'],
            'viewer_count': stream_data['viewer_count']
        } for stream_data in streams
    ]


async def _post_stream_embed(channel_id: str, embed: dict, content=None):
    try:
        await bot.api_post(f'/channels/{channel_id}/messages', data={'content': content, 'embeds': [embed]})
    except HTTPRequestStatusError:
        pass


def _stream_to_embed(stream: dict) -> dict:
    return {
        "color": 6570405,
        "title": stream['title'],
        "url": "https://twitch.tv/" + stream['user_name'],
        "image": {"url": stream['thumbnail'].format(width='320', height='180')},
        "author": {'name': stream['user_name'], 'icon_url': stream['user_avatar']},
        "thumbnail": {'url': stream['game_thumbnail'].format(width='144', height='192')},
        "footer": {'text': 'Started at'},
        "timestamp": datetime.fromtimestamp(stream['started_at']).isoformat(),
        "fields": [
            {"name": "**Game**", "value": f"{stream['game_name']}", "inline": True},
            {"name": "**Viewers**", "value": f"{stream['viewer_count']}", "inline": True}
        ]
    }


def _stream_summary_embed(stream: dict, stream_stat: dict) -> dict:
    return {
        "color": 6570405,
        "title": stream['title'],
        "author": {"name": stream['user_name'] + "'s stream summary", "icon_url": stream['user_avatar']},
        "thumbnail": {'url': stream['thumbnail'].format(width='320', height='180')},
        "fields": [
            {"name": "Stream duration", "value": str(timedelta(seconds=int(time())-stream['started_at'])), "inline": False},
            {"name": "Average viewers", "value": f"{int(stream_stat['average'])}", "inline": True},
            {"name": "Peak viewers", "value": f"{stream_stat['peak']}", "inline": True}
        ]
    }


@bot.on_think
async def twitch_think(frame_time: float):
    global LAST_TWITCH_POLL
    if frame_time - LAST_TWITCH_POLL < TWITCH_POLL_DELAY:
        return
    LAST_TWITCH_POLL = frame_time
    await twitch_poll()


async def twitch_poll():
    logger.warning('Polling twitch...')
    now = int(time())

    # Get all twitch user_names to fetch streams for
    channel_to_guilds = defaultdict(list)
    for g in bot.guilds.values():
        for i in g.cfg.twitch_channels:
            channel_to_guilds[i['channel']].append(g)

    # Fetch data from twitch and local db
    live_streams = await _fetch_twitch_streams(*channel_to_guilds.keys())
    known_streams = await db.select('twitch_streams', {'is_live': True})

    # Update streams which is no longer live or no longer need to be tracked
    live_streams_ids = [i['stream_id'] for i in live_streams]
    for stream in filter(lambda i: i['stream_id'] not in live_streams_ids, known_streams):
        stream_stat = await db.fetch_one(
            "SELECT MAX(`viewer_count`) as peak, AVG(`viewer_count`) as average" +
            "\nFROM `twitch_stat` WHERE `stream_id`=%s",
            (stream['stream_id'],)
        )
        await db.update('twitch_streams', data={'is_live': False}, where={'stream_id': stream['stream_id']})
        for guild in channel_to_guilds.get(stream['user_name']):
            await _post_stream_embed(
                guild.cfg.twitch_announcement_channel or guild.id,
                embed=_stream_summary_embed(stream, stream_stat)
            )

    known_streams_ids = [i['stream_id'] for i in known_streams]
    for stream in live_streams:

        # Update an existing stream
        if stream['stream_id'] in known_streams_ids:
            await db.update('twitch_streams', data=stream, where={'stream_id': stream['stream_id']})
            await db.insert(
                'twitch_stat',
                {'stream_id': stream['stream_id'], 'viewer_count': stream['viewer_count'], 'at': now}
            )
            continue

        # Save and post announcements for new stream
        await db.insert('twitch_streams', stream)
        for guild in channel_to_guilds.get(stream['user_name']):
            config_row = find(lambda i: i['channel'] == stream['user_name'], guild.cfg.twitch_channels)
            if not config_row:  # config could have been updated during the data fetch
                continue
            await _post_stream_embed(
                channel_id=guild.cfg.twitch_announcement_channel or guild.id,
                content=config_row['message_text'] if len(config_row['message_text'] or '') else None,
                embed=_stream_to_embed(stream),
            )
