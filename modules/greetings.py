from __future__ import annotations
from typing import TYPE_CHECKING
from nextcore.http.errors import HTTPRequestStatusError

from db import db
from bot import bot

if TYPE_CHECKING:
    from discord_typings import GuildMemberAddData, GuildMemberRemoveData


async def _send_message(channel_id: str, content: str):
    try:
        await bot.api_post(f'/channels/{channel_id}/messages', data={'content': content})
    except HTTPRequestStatusError:
        pass


@bot.event_dispatcher.listen('GUILD_MEMBER_ADD')
async def on_member_add(data: GuildMemberAddData):
    counter = await db.select_one('greetings', {'guild_id': data['guild_id'], 'user_id': data['user']['id']})
    counter = counter or {'guild_id': data['guild_id'], 'user_id': data['user']['id'], 'visit_count': 0}
    counter['visit_count'] += 1
    await db.insert('greetings', counter, on_conflict='replace')

    guild = bot.guilds.get(data['guild_id'])
    if not guild or not guild.cfg.greetings_enable:
        return

    if not guild.cfg.greetings_welcome_channel:
        return

    if counter['visit_count'] > 1 and guild.cfg.greetings_welcome_back_message:
        await _send_message(
            guild.cfg.greetings_welcome_channel,
            guild.cfg.greetings_welcome_back_message.format(
                member=f"<@{counter['user_id']}>", count=counter['visit_count']
            )
        )
    elif guild.cfg.greetings_welcome_message:
        await _send_message(
            guild.cfg.greetings_welcome_channel,
            guild.cfg.greetings_welcome_message.format(member=f"<@{counter['user_id']}>")
        )


@bot.event_dispatcher.listen('GUILD_MEMBER_REMOVE')
async def on_member_remove(data: GuildMemberRemoveData):
    guild = bot.guilds.get(data['guild_id'])
    if not guild or not guild.cfg.greetings_enable or not guild.cfg.greetings_goodbye_channel:
        return

    counter = await db.select_one('greetings', {'guild_id': data['guild_id'], 'user_id': data['user']['id']})
    counter = counter or {'guild_id': data['guild_id'], 'user_id': data['user']['id'], 'visit_count': 0}
    if counter['visit_count'] > 1 and guild.cfg.greetings_goodbye_again_message:
        await _send_message(
            guild.cfg.greetings_goodbye_channel,
            guild.cfg.greetings_goodbye_again_message.format(
                member=f"{data['user']['username']}", count=counter['visit_count']
            )
        )
    elif guild.cfg.greetings_goodbye_message:
        await _send_message(
            guild.cfg.greetings_goodbye_channel,
            guild.cfg.greetings_goodbye_message.format(
                member=f"{data['user']['username']}"
            )
        )
