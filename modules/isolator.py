from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
import re
from time import time
from datetime import timedelta
from nextcore.http.errors import HTTPRequestStatusError

from common import parse_duration
from db import db
from bot import bot, FakeMember
from bot.errors import BotNotFoundError, BotSyntaxError, BotValueError

if TYPE_CHECKING:
    from discord_typings import GuildMemberAddData, GuildMemberRemoveData
    from bot import Guild, SlashCommandInteraction, SlashAutocompleteInteraction


logger = getLogger(__name__)
ISOLATOR_CHECK_DELAY = 30
LAST_ISOLATOR_CHECK = time()


async def _add_roles(guild: Guild, user_id: int | str, isolated: bool, muted: bool):
    if (member := await guild.fetch_member(str(user_id))) is None:
        return
    if isolated and guild.cfg.isolator_role and guild.cfg.isolator_role not in member.roles:
        try:
            await bot.api_put(f"/guilds/{guild.id}/members/{member.id}/roles/{guild.cfg.isolator_role}", data={})
        except HTTPRequestStatusError:
            pass
    if muted and guild.cfg.isolator_mute_role and guild.cfg.isolator_mute_role not in member.roles:
        try:
            await bot.api_put(f"/guilds/{guild.id}/members/{member.id}/roles/{guild.cfg.isolator_mute_role}", data={})
        except HTTPRequestStatusError:
            pass


async def _remove_roles(guild: Guild, user_id: int | str, isolated: bool, muted: bool):
    if (member := await guild.fetch_member(str(user_id))) is None:
        return
    if not isolated and guild.cfg.isolator_role and guild.cfg.isolator_role in member.roles:
        try:
            await bot.api_delete(f"/guilds/{guild.id}/members/{member.id}/roles/{guild.cfg.isolator_role}")
        except HTTPRequestStatusError:
            pass
    if not muted and guild.cfg.isolator_mute_role and guild.cfg.isolator_mute_role in member.roles:
        try:
            await bot.api_delete(f"/guilds/{guild.id}/members/{member.id}/roles/{guild.cfg.isolator_mute_role}")
        except HTTPRequestStatusError:
            pass


async def _post_audit_string(guild: Guild, string: str):
    if not guild.cfg.isolator_log_channel or guild.cfg.isolator_log_channel not in guild.channels:
        return
    try:
        await bot.api_post(f'/channels/{guild.cfg.isolator_log_channel}/messages', data={'content': string})
    except HTTPRequestStatusError:
        pass


@bot.slash_command('isolator isolate')
async def isolate(sci: SlashCommandInteraction, user: str, duration: str, reason: str = None):

    # Get prisoner data
    if (mention := re.match(r"^<@!?(\d+)>$", user)) is not None:
        if (member := await sci.guild.fetch_member(mention.group(1))) is None:
            raise BotNotFoundError('Server member not found. Use user_id:username mask for missing members.')
    elif (user_mask := re.match(r"(\d+):(.*)", user)) is not None:
        member = FakeMember(user_id=user_mask.group(1), username=user_mask.group(2))
    else:
        raise BotSyntaxError("You must specify a member highlight or a user_id:name mask.")

    # Parse duration
    try:
        duration = parse_duration(duration)
    except ValueError:
        raise BotSyntaxError(f"Incorrect duration format '{duration}'. Format: 34[m|h|d|W|M|Y] or inf.")
    if duration < 0 or duration > 311040000:
        raise BotValueError("Duration must be lesser that 10 years, bud.")

    # Update existing isolator record if possible
    case = await db.select_one(
        'isolator',
        {'guild_id': sci.guild.id, 'user_id': member.id, 'is_active': True}
    )
    if case is not None:
        update_data = {
            'user_id': member.id, 'duration': duration,
            'author_id': sci.author.id, 'author_username': sci.author.username
        }
        if reason:
            update_data['reason'] = reason
        await db.update('isolator', where={'case_id': case['case_id']}, data=update_data)
        await sci.reply(f"Updated `{case['username']}`'s case.")
        await _add_roles(sci.guild, member.id, isolated=True, muted=case['is_muted'])
        await _post_audit_string(
            sci.guild,
            "`{author}` has updated `{prisoner}`'s case. New duration: `{left}`.{reason}".format(
                author=sci.author.username,
                prisoner=case['username'],
                left=timedelta(seconds=duration) if duration else '∞',
                reason=f" {reason}." if reason else ''
            )
        )
        return

    # Create new isolator record
    await db.insert(
        'isolator',
        {
            'guild_id': sci.guild.id,
            'user_id': member.id,
            'username': member.username,
            'name': member.display_name,
            'at': int(time()),
            'duration': duration,
            'author_id': sci.author.id,
            'author_username': sci.author.username,
            'reason': reason
        }
    )
    await sci.reply(f'`{member.username}` is taken to the isolation ward.')
    await _add_roles(sci.guild, member.id, isolated=True, muted=False)
    await _post_audit_string(sci.guild, "`{author}` has isolated `{prisoner}`. Duration: `{left}`.{reason}".format(
        author=sci.author.username,
        prisoner=member.username,
        left=timedelta(seconds=duration) if duration else '∞',
        reason=f" {reason}." if reason else ''
    ))


@bot.slash_command('isolator release')
async def release(sci: SlashCommandInteraction, prisoner: str, comment: str = None):
    case = await db.select_one('isolator', {'guild_id': sci.guild.id, 'username': prisoner, 'is_active': True})
    if case is None:
        raise BotNotFoundError(f'`{prisoner}` is not found.')
    await db.update('isolator', where={'case_id': case['case_id']}, data={'is_active': False})
    await sci.reply(f'`{prisoner}` is released from the isolation ward.')
    await _remove_roles(sci.guild, case['user_id'], isolated=False, muted=False)
    await _post_audit_string(sci.guild, "`{author}` has released `{prisoner}`{comment}".format(
        author=sci.author.username,
        prisoner=prisoner,
        comment=f" ({comment})." if comment else '.'
    ))


@bot.slash_command('isolator mute')
async def mute(sci: SlashCommandInteraction, prisoner: str, comment: str = None):
    case = await db.select_one('isolator', {'guild_id': sci.guild.id, 'username': prisoner, 'is_active': True})
    if case is None:
        raise BotNotFoundError(f'Prisoner with username `{prisoner}` is not found.')
    await db.update('isolator', where={'case_id': case['case_id']}, data={'is_muted': True})
    await sci.reply(f'`{prisoner}` is now muted.')
    await _add_roles(sci.guild, case['user_id'], isolated=True, muted=True)
    await _post_audit_string(sci.guild, "`{author}` has muted `{prisoner}`{comment}".format(
        author=sci.author.username,
        prisoner=prisoner,
        comment=f" ({comment})." if comment else '.'
    ))


@bot.slash_command('isolator unmute')
async def unmute(sci: SlashCommandInteraction, prisoner: str, comment: str = None):
    case = await db.select_one('isolator', {'guild_id': sci.guild.id, 'username': prisoner, 'is_active': True})
    if case is None:
        raise BotNotFoundError(f'Prisoner with username `{prisoner}` is not found.')
    await db.update('isolator', where={'case_id': case['case_id']}, data={'is_muted': False})
    await sci.reply(f'`{prisoner}` is now unmuted.')
    await _remove_roles(sci.guild, case['user_id'], isolated=True, muted=False)
    await _post_audit_string(sci.guild, "`{author}` has unmuted `{prisoner}`{comment}".format(
        author=sci.author.username,
        prisoner=prisoner,
        comment=f" ({comment})." if comment else '.'
    ))


@bot.slash_command('isolator list')
async def list_isolator(sci: SlashCommandInteraction):
    prisoners = await db.select('isolator', {'guild_id': sci.guild.id, 'is_active': True})
    now = int(time())
    s = "```markdown"
    s += "\n ID | Prisoner | User ID | Left | Reason"
    s += "\n----------------------------------------"
    if not len(prisoners):
        await sci.reply_raw(content=s+'\n Isolation ward is empty.```')
        return
    for case in prisoners:
        s += "\n{} | {}{} | {} | {} | {}".format(
            case['case_id'],
            f"{case['name'] or '-'} ({case['username']})",
            '🔇' if case['is_muted'] else '',
            case['user_id'],
            timedelta(seconds=(case['at']+case['duration']-now)) if case['duration'] else '∞',
            case['reason'] or '-'
        )
    await sci.reply_raw(content=s+'```')


@bot.slash_autocomplete('prisoner')
async def autocomplete_prisoner(sai: SlashAutocompleteInteraction) -> list[dict]:
    return [
        {'name': f"{case['name'] or '-'} ({case['username']})", 'value': case['username']}
        for case in await db.select('isolator', {'guild_id': sai.guild.id, 'is_active': True})
        if case['username'].find(sai.value) >= 0
    ][:25]


@bot.event_dispatcher.listen('GUILD_MEMBER_ADD')
async def on_member_add(data: GuildMemberAddData):
    guild = bot.guilds.get(data['guild_id'])
    case = await db.select_one(
        'isolator',
        {'guild_id': data['guild_id'], 'user_id': data['user']['id'], 'is_active': True}
    )
    if not case or not guild:
        return
    await _add_roles(guild, data['user']['id'], True, case['is_muted'])
    await _post_audit_string(guild, "`{prisoner}` tried to join the server, but ended up in the isolation ward".format(
        prisoner=case['username']
    ))


@bot.event_dispatcher.listen('GUILD_MEMBER_REMOVE')
async def on_member_remove(data: GuildMemberRemoveData):
    guild = bot.guilds.get(data['guild_id'])
    case = await db.select_one(
        'isolator',
        {'guild_id': data['guild_id'], 'user_id': data['user']['id'], 'is_active': True}
    )
    if not case or not guild:
        return
    await _post_audit_string(guild, "Prisoner `{prisoner}` left the server.".format(
        prisoner=case['username']
    ))


@bot.on_think
async def check_isolator(frame_time: float):
    global LAST_ISOLATOR_CHECK
    if frame_time - LAST_ISOLATOR_CHECK < ISOLATOR_CHECK_DELAY:
        return
    LAST_ISOLATOR_CHECK = frame_time
    to_release_cases = await db.fetch_all(
        'SELECT * FROM `isolator` WHERE `is_active`=1 AND `at`+`duration` < %s',
        (int(frame_time),)
    )
    for case in to_release_cases:
        await _release_expired_case(case)


async def _release_expired_case(case: dict):
    await db.update('isolator', data={'is_active': False}, where={'case_id': case['case_id']})

    if (guild := bot.guilds.get(str(case['guild_id']))) is None:
        logger.warning(f"Missing guild {case['guild_id']} for an isolator record {case['case_id']}.")
        return

    if (member := guild.members.get(str(case['user_id']))) is None:
        await _post_audit_string(
            guild,
            "Missing prisoner `{prisoner}` record has expired (the time served has passed).".format(
                prisoner=case['username']
            ))
        return

    await _post_audit_string(
        guild,
        "Prisoner `{prisoner}` was released from the isolation ward (the time served has expired).".format(
            prisoner=case['username']
        ))
    await _remove_roles(guild, member.id, isolated=False, muted=False)
