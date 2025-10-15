import logging
from aiohttp import ClientSession
from time import time

import config
from db import db
from bot import bot, Guild
from common import random_string

from .utils import ApiError

logger = logging.getLogger(__name__)
oauth2_uri = 'https://discord.com/api/oauth2/token'
identify_uri = 'https://discord.com/api/users/@me'
guilds_uri = 'https://discord.com/api/users/@me/guilds'

"""
This module implements user authentication via discord oauth2 api. Steps:
1. From discord app authorization page user gets redirected to cfg.API_OAUTH_REDIRECT_URI?code=XXXX.
2. On the page user makes post request to do_oauth with the code.
3. _oauth_verify confirms from discord API if the code is correct and receives user_data with user access_token.
4. _oauth_fetch_user fetches user_data from the discord API (username, avatar, etc...) with the access_token.
5. do_oauth generates user api_token, replaces or creates new user in the db oauth table.
6. api_token is passed back to the user for further interactions.
Update user_data each time user_data['access_token'] is expired (@refresh_user decorator). 
"""


async def do_oauth(code: str) -> dict:
    logger.info(f"API| Trying to auth a dc user with received oauth2 code '{code}'")
    oauth_data = await _oauth_verify(code, config.API_OAUTH_REDIRECT_URI, config.API_OAUTH_SCOPES)
    user_data = await _oauth_fetch_user(oauth_data['access_token'])

    await db.delete('oauth_user', {'user_id': user_data['id']})
    oauth_user = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'discriminator': user_data['discriminator'],
        'avatar': user_data['avatar'],
        'api_token': random_string(8),  # TODO: make sure this is unique
        'access_token': oauth_data['access_token'],
        'refresh_token': oauth_data['refresh_token'],
        'expires_at': int(time()) + oauth_data['expires_in']
    }
    await db.insert('oauth_user', oauth_user)
    return oauth_user


async def _oauth_verify(oauth_code: str, redirect_uri: str, scopes: list[str]) -> dict:
    """
    Verify oauth_code on the discord server.
    Returns oauth data response in format:
        {"access_token": str, "expires_in": int, "refresh_token": str, "scope": "identify guilds", "token_type": "Bearer" }
    """

    data = {
        'client_id': config.DC_CLIENT_ID,
        'client_secret': config.DC_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': oauth_code,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes)
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with ClientSession() as session:
        async with session.post(oauth2_uri, data=data, headers=headers) as resp:
            # Response status should be 200 if oauth_code is legit
            if resp.status != 200:
                logger.error("API| Got invalid oauth2 code {}, got {} response code from discord api.".format(oauth_code,
                                                                                                           resp.status))
                raise ApiError(400, 'Bad Request', 'Failed to authenticate.')

            oauth_data = await resp.json()
            # Check the scopes are correct
            if set(oauth_data['scope'].split(' ')) != set(scopes):
                logger.error(
                    "API| Invalid scope '{}' provided for oauth2 code '{}'".format(oauth_data['scope'], oauth_code))
                raise ApiError(400, 'Bad Request', 'Invalid oauth2 scopes provided.')

    # All good
    return oauth_data


async def _oauth_fetch_user(access_token) -> dict:
    """
    Fetch user identity using the access_token from _oauth_verify().
    Returns user data response in format:
        {
            "id": str, "username": str, "avatar": "3eec9254791b69687d29d4b2546dec7f", "discriminator": str,
            "public_flags": 0, "flags": 0, "locale": "ru", "mfa_enabled": false
        }
    """

    headers = {'Authorization': 'Bearer ' + access_token}
    async with ClientSession() as session:
        async with session.get(identify_uri, headers=headers) as resp:
            if resp.status != 200:
                logger.error(
                    "API| Error fetching user identity for access_token '{}', got {} response code from discord api".format(
                        access_token, resp.status))
                raise ApiError(500, 'Discord API error', 'Error fetching user identity')
            return await resp.json()


def refresh_user(coro):
    """ This decorator refreshes user access_token and other data on demand (if token has expired) """

    async def _update_user(oauth_user: dict) -> dict:
        # Get new user data
        data = {
            'client_id': config.DC_CLIENT_ID,
            'client_secret': config.DC_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': oauth_user['refresh_token']
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        logger.info(data)

        async with ClientSession() as session:
            async with session.post('https://discord.com/api/v8/oauth2/token', data=data, headers=headers) as resp:
                if resp.status != 200:
                    logger.error(
                        'API| got invalid oauth2 refresh_token \'{}\', got {} response code from discord api'.format(
                            data['refresh_token'], resp.status
                        ))
                    raise ApiError(401, 'Bad Request', 'Failed to authenticate.')
                oauth_data = await resp.json()

        # Confirm the user_ids are matching
        if oauth_data['id'] != oauth_user['user_id']:
            logger.error('API| user_id mismatching @ \'{}\' refresh_token update, expected {} got {}.'.format(
                data['refresh_token'], oauth_user['user_id'], oauth_data['id']))
            raise ApiError(401, 'Bad Request', 'Failed to authenticate.')

        # Push to database

        new_oauth_user = {
            'user_id': oauth_data['id'],
            'username': oauth_data['username'],
            'discriminator': oauth_data['discriminator'],
            'avatar': oauth_data['avatar'],
            'api_token': oauth_user['api_token'],
            'access_token': oauth_data['access_token'],
            'refresh_token': oauth_data['refresh_token'],
            'expires_at': int(time()) + oauth_data['expires_in']
        }
        await db.insert('oauth_user', new_oauth_user, on_conflict='replace')
        return new_oauth_user

    async def wrapper(oauth_user: dict, *args, **kwargs):
        if oauth_user['expires_at'] < time():
            oauth_user = await _update_user(oauth_user)
        return await coro(oauth_user, *args, **kwargs)

    return wrapper


@refresh_user
async def fetch_user_guilds(oauth_user: dict) -> list[int]:
    """
    Fetch user's guild list from discord api. API response format:
        [{"id": str, "name": str, "icon": "8342729096ea3675442027381ff50dfe", "owner": true, "permissions": "36953089", "features": ["COMMUNITY", "NEWS"]}]
    Updates oauth_user_guilds for the lazy method.
    Returns list with discord.Guild objects.
    """

    headers = {'Authorization': 'Bearer ' + oauth_user['access_token']}
    async with ClientSession() as session:
        async with session.get(guilds_uri, headers=headers) as resp:
            if resp.status != 200:
                logger.error(
                    f"API| Error fetching guilds list for access_token '{oauth_user['access_token']}', resp.code {resp.status}"
                )
                raise ApiError(500, 'Discord API error', 'Error fetching guild list.')
            guilds_data = await resp.json()

    await db.delete('oauth_user_guilds', {'user_id': oauth_user['user_id']})
    await db.insert_many(
        'oauth_user_guilds',
        ['user_id', 'guild_id'],
        ([oauth_user['user_id'], g['id']] for g in guilds_data)
    )
    return [g['id'] for g in guilds_data]


async def get_user_guilds(oauth_user: dict) -> list[Guild]:
    """ Get user guilds from db (lazy method) """
    guild_ids = [str(i['guild_id']) for i in await db.select('oauth_user_guilds', {'user_id': oauth_user['user_id']})]
    logger.info(f'guild_ids={guild_ids}')
    return [g for g in bot.guilds if g.id in guild_ids]


async def get_user(api_token: str) -> dict:
    """ Return oauth_user data for an api_token or raise an exception """
    if (oauth_user := await db.select_one('oauth_user', {'api_token': api_token})) is None:
        raise ApiError(400, 'API error', 'Bad api_token.')
    return oauth_user


async def delete_user(oauth_user: dict) -> None:
    await db.delete('oauth_user', {'user_id': oauth_user['user_id']})
