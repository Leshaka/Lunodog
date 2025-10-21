from __future__ import annotations
from typing import TYPE_CHECKING

import json
import GeoIP
import re
import socket
import aiohttp
from time import time
from collections import defaultdict
from string import Formatter
from logging import getLogger

from common import escape_markdown, gather_with_pool
from utils import qstat
from bot import bot, errors


if TYPE_CHECKING:
    from bot import SlashCommandInteraction, Guild


logger = getLogger(__name__)
formatter = Formatter()
geoip = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
DEFAULT_QSTAT_STRING = "{flag_icon} [**{modname}**] {mapname} {private_icon}`/connect {host}` | `{name}`: `{p_string}`"
IP_API_CACHE: dict[str, str] = dict()
IP_API_LAST_REQUESTS: list[float] = []


def host_to_ip(host: str) -> str:
    try:
        socket.inet_aton(host)
        return host
    except socket.error:
        try:
            return socket.gethostbyname(host)
        except Exception:
            raise ValueError(f"Invalid host: {host}")


async def query_with_hostname(hostname: str, address: str, port: int, timeout: int = 5):
    """ Adds _hostname key to PromodeQuerier.queryServerAsync() data """
    res = await qstat.query_server(address, port, timeout=timeout)
    if res is not None:
        res['_hostname'] = hostname
    return res


async def query_servers(servers: dict[tuple[str, int], str | None], m_servers: list[tuple[str, int]]) -> list[dict]:
    """ Query master servers first, then query combined list of provided servers with master servers server list
    Args:
        servers: A dictionary with {(ip_address, port): hostname} data. Hostname can be None in case there is no hostname.
        m_servers: A master server list with [(ip_address, port)] data.
    Returns:
         List of servers data from PromodeQuerier.queryServerAsync() with additional '_hostname' field.
    """

    ignore_exceptions = (TimeoutError, ValueError, IndexError)
    do_query_masters = gather_with_pool(
        tasks=(qstat.query_master(*i, timeout=2) for i in m_servers),
        pool_size=min([5, len(m_servers)]),
        ignore_exceptions=ignore_exceptions
    )
    for resp in await do_query_masters:
        if resp:
            for srv in resp:
                if srv not in servers:
                    servers[srv] = None

    res = []
    do_query_servers = gather_with_pool(
        tasks=(query_with_hostname(v, *k, timeout=1) for k, v in servers.items()),
        pool_size=min([50, len(servers)]),
        ignore_exceptions=ignore_exceptions
    )
    for server in await do_query_servers:
        if server is not None:
            res.append(server)
    return res


async def inject_flag_icons(guild: Guild, servers: list[dict]):
    """
    Adds 'flag_icon' field to servers (list of qstat.query_server responses).
    This method has multiple fallbacks:
        - use custom flag icon string from guild config if set
        - use cached flag icon from ip-api.com database if exists
        - fetch missing flag icons from ip-api.com if we are not hitting the api limits (15 per minute)
        - get missing flag icons from local GeoIP database as last fallback
    """
    global IP_API_LAST_REQUESTS

    # get custom flag icons from guild config or local ip-api.com cache
    custom_icons = {i['host']: i['flag'] for i in guild.cfg.qstat_servers if i['flag'] not in (None, '')}
    for i in servers:
        i['flag_icon'] = custom_icons.get(i['_hostname']) or IP_API_CACHE.get(i['address'])

    missing = [i for i in servers if i.get('flag_icon') is None]
    if not len(missing):
        return

    # fetch flags from ip-api.com
    if len(IP_API_LAST_REQUESTS) < 15 or IP_API_LAST_REQUESTS[14] < time()-55:
        logger.debug('Fetching flags from ip-api.com...')
        payload = list(set((i['address'] for i in missing)))
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('http://ip-api.com/batch?countryCode', json=payload) as response:
                    data = await response.json()
        except Exception as e:
            logger.error(f"Failed to fetch data from ip-api.com: {e}.")
        else:
            for n in range(len(payload)):
                IP_API_CACHE[payload[n]] = ':flag_' + data[n]['countryCode'].lower() + ':'
            for i in missing:
                i['flag_icon'] = IP_API_CACHE[i['address']]
            return
        finally:
            IP_API_LAST_REQUESTS.insert(0, time())
            IP_API_LAST_REQUESTS = IP_API_LAST_REQUESTS[:15]
    else:
        logger.warning('Reached api limits for ip-api.com.')

    logger.warning('Using local GeoIP database.')
    for i in missing:
        country_code = geoip.country_code_by_addr(i['address'])
        i['flag_icon'] = f':flag_{country_code.lower()}:' if country_code else ':grey_question:'


async def do_qstat(sci: SlashCommandInteraction, fast: bool = None):
    if not sci.guild.cfg.qstat_enable:
        raise errors.BotPermissionError('The /qstat command is turned off on this server.')

    if not fast:
        m_servers = [(host_to_ip(i['host']), i['port']) for i in sci.guild.cfg.qstat_master_servers]
    else:
        m_servers = []
    hosts = {(host_to_ip(i['host']), i['port']): i['host'] for i in sci.guild.cfg.qstat_servers}

    servers = []
    for srv in await query_servers(hosts, m_servers):
        # filter by json filter
        if sci.guild.cfg.qstat_filter:
            filt = json.loads(sci.guild.cfg.qstat_filter)
            if any((srv.get(key) != filt[key] for key in filt.keys())):
                continue

        # frick this one
        if srv['address'] == '138.2.130.215':
            continue

        srv['players'] = srv['players'] or []
        # convert players list into a readable string
        srv['p_string'] = ', '.join([
            escape_markdown(i['name'])
            for i in srv['players']
        ]) if len(srv['players']) else 'no players'

        if len(srv['players']) == 0 and not sci.guild.cfg.qstat_show_empty:
            continue

        if len(srv['players']) >= srv.get('sv_maxclients', 100) and not sci.guild.qstat_show_full:
            continue

        srv['private_icon'] = "🔒" if srv.get('g_needpass') else ' '
        srv['name'] = re.sub(r"\^[^ ]", '', srv['sv_hostname'])
        srv['modname'] = srv.get('game') or srv.get('gamename') or ' '
        srv['numclients'] = len(srv['players'])
        srv['host'] = f"{srv['_hostname'] or srv['address']}:{srv['port']}"
        servers.append(srv)

    if not len(servers):
        raise errors.BotNotFoundError('No servers to display.')

    servers = sorted(servers, key=lambda i: i.get(sci.guild.cfg.qstat_sortby))[:10]
    await inject_flag_icons(sci.guild, servers)
    await sci.reply_raw(content='\n'.join([
        formatter.vformat(
            sci.guild.cfg.qstat_string or DEFAULT_QSTAT_STRING,
            (),
            defaultdict(lambda: '-', i)
        ) for i in servers
    ]))


bot.slash_command('qstat', expensive=True)(do_qstat)
bot.slash_command('servers', expensive=True)(do_qstat)
