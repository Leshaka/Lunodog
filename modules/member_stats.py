from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from time import time
from datetime import timedelta

from bot import bot
from bot import errors
from db import db
from common import parse_user_mention, Colors

if TYPE_CHECKING:
    from discord_typings import MessageCreateData, PresenceUpdateData, MessageReactionAddData, MessageReactionRemoveData
    from bot import SlashCommandInteraction, MemberPresence

"""
Guild member stats profile.
"""

logger = getLogger(__name__)


@bot.event_dispatcher.listen('MESSAGE_CREATE')
async def on_message(data: MessageCreateData):
    # skip messages from webhooks and DMs
    if 'member' not in data or 'guild_id' not in data:
        return

    # skip messages of miscellaneous types
    if data['type'] not in [0, 19]:  # regular message or reply
        return

    # if the message is a reply get user_id of the referenced message author
    if data['type'] == 19 and (ref := data.get('referenced_mesage')) is not None:
        reply_to_user = None if ref.get('webhook_id') else ref['author']['id']
    else:
        reply_to_user = None

    await db.insert(
        'mbr_stats_messages',
        {
            'guild_id': data['guild_id'],
            'channel_id': data['channel_id'],
            'user_id': data['author']['id'],
            'message_id': data['id'],
            'reply_to_user': reply_to_user,
            'at': int(time())
        }
    )


@bot.event_dispatcher.listen('MESSAGE_REACTION_ADD')
async def on_reaction_add(data: MessageReactionAddData):
    # skip DMs
    if 'guild_id' not in data:
        return

    await db.insert(
        'mbr_stats_reactions',
        {
            'guild_id': data['guild_id'],
            'message_id': data['message_id'],
            'message_author_id': data.get('message_author_id'),  # this could be missing on webhook messages
            'user_id': data['user_id'],
            'emoji': data['emoji']['name'],
            'emoji_id': data['emoji']['id'],
            'at': int(time())
        }
    )


@bot.event_dispatcher.listen('MESSAGE_REACTION_REMOVE')
async def on_reaction_remove(data: MessageReactionRemoveData):
    # skip DMs
    if 'guild_id' not in data:
        return

    emoji_id = data['emoji']['id']
    await db.delete(
        'mbr_stats_reactions',
        {
            'user_id': data['user_id'],
            'message_id': data['message_id'],
            # delete either by emoji_id if exists or by emoji name
            **({'emoji_id': emoji_id} if emoji_id is not None else {'emoji': data['emoji']['name']})
        }
    )


@bot.event_dispatcher.listen('BOT_MEMBER_PRESENCE_CHANGE')
async def on_bot_member_presence_change(old_presence: MemberPresence, presence_data: PresenceUpdateData):
    if old_presence.status == presence_data['status']:
        return

    now = int(time())
    await db.insert(
        'mbr_stats_presence',
        {
            'guild_id': presence_data['guild_id'],
            'user_id': presence_data['user']['id'],
            'status': old_presence.status,
            'started_at': old_presence.at,
            'ended_at': now,
            'duration': now-old_presence.at
        }
    )

    if presence_data['status'] == 'offline':
        await db.insert(
            'mbr_stats_last_logoff',
            {
                'guild_id': presence_data['guild_id'],
                'user_id': presence_data['user']['id'],
                'at': now
            },
            on_conflict='replace'
        )


@bot.on_close()
async def on_bot_close():
    logger.info('Saving presences...')
    now = int(time())
    for guild in bot.guilds.values():
        await db.insert_many(
            'mbr_stats_presence',
            ['guild_id', 'user_id', 'status', 'started_at', 'ended_at', 'duration'],
            [
                [guild.id, user_id, presence.status, presence.at, now, now-presence.at]
                for user_id, presence in guild.presences.items()
            ]
        )


@bot.slash_command('profile')
async def show_member_profile(sci: SlashCommandInteraction, user: str):
    target = sci.get_resolved_member(user)
    now = int(time())
    at_after = now-60*60*24*30
    messages_cnt = (await db.fetch_one(
        "SELECT COUNT(*) as cnt FROM mbr_stats_messages WHERE guild_id=%s AND user_id=%s AND at>%s",
        (sci.guild.id, target.id, at_after)
    ))['cnt']
    replies_cnt = (await db.fetch_one(
        "SELECT COUNT(*) as cnt FROM mbr_stats_messages WHERE guild_id=%s AND reply_to_user=%s AND user_id!=%s AND at>%s",
        (sci.guild.id, target.id, target.id, at_after)
    ))['cnt']
    reactions_sent_cnt = (await db.fetch_one(
        "SELECT COUNT(*) as cnt FROM mbr_stats_reactions WHERE guild_id=%s AND user_id=%s AND at>%s",
        (sci.guild.id, target.id, at_after)
    ))['cnt']
    reactions_recv_cnt = (await db.fetch_one(
        "SELECT COUNT(*) as cnt FROM mbr_stats_reactions WHERE guild_id=%s AND message_author_id=%s AND user_id!=%s AND at>%s",
        (sci.guild.id, target.id, target.id, at_after)
    ))['cnt']

    presences_stats = await db.fetch_all(
        "SELECT status, SUM(duration) as duration FROM mbr_stats_presence WHERE guild_id=%s AND user_id=%s AND started_at>%s GROUP BY status",
        (sci.guild.id, target.id, at_after)
    )
    presences = {'online': 0, 'idle': 0, 'dnd': 0, 'offline': 0}
    if (presence_now := sci.guild.presences.get(target.id)) is not None:
        presences[presence_now.status] = now - presence_now.at
    for i in presences_stats:
        presences[i['status']] += i['duration']
    presences_total = sum(presences.values())
    presences = {i: int((presences[i] / presences_total) * 100) for i in presences}

    emojis = await db.fetch_all(
        "SELECT emoji, emoji_id, COUNT(*) as cnt FROM mbr_stats_reactions WHERE guild_id=%s AND user_id=%s AND at>%s GROUP BY emoji collate utf8mb4_unicode_520_ci ORDER BY cnt DESC LIMIT 3",
        (sci.guild.id, target.id, at_after)
    )
    emojis = [
        (f"<:{i['emoji']}:{i['emoji_id']}>" if i['emoji_id'] else i['emoji']) + f" __{i['cnt']}__"
        for i in emojis
    ]

    last_logoff = await db.select_one('mbr_stats_last_logoff', {'guild_id': sci.guild.id, 'user_id': target.id})
    last_logoff = f"{timedelta(seconds=now-last_logoff['at'])} ago" if last_logoff else 'no data'

    embed = dict(
        color=Colors.DISCORD,
        title=target.display_name,
        description=f"@{target.username} ({target.id})\n\u200b",
        thumbnail={'url': f'https://cdn.discordapp.com/avatars/{target.id}/{target.avatar}.webp?size=256'},
        fields=[
            {
                'name': 'Activity',
                'value': f'__**{messages_cnt}**__ messages\n__**{reactions_sent_cnt}**__ reactions\n\u200b',
                'inline': True,
            },
            {
                'name': 'Popularity',
                'value': f'__**{replies_cnt}**__ replies\n__**{reactions_recv_cnt}**__ reactions',
                'inline': True,
            },
            {
                'name': 'Presence',
                'value': '\n'.join((
                    f"🟢 online - {presences['online']}%",
                    f"🟡 idle - {presences['idle']}%",
                    f"🔴 dnd - {presences['dnd']}%",
                    f"⚫ offline - {presences['offline']}%"
                )) + '\n\u200b',
            },
            {
                'name': 'Favorite reactions',
                'value': ('\n'.join(emojis) if len(emojis) else 'no data') + '\n\u200b'
            },
            {
                'name': 'Last logoff',
                'value': f'{last_logoff}\n\u200b'
            }
        ],
        footer={'text': 'Monthly stats'}
    )
    await sci.reply_raw(embeds=[embed])
