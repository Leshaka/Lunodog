from __future__ import annotations
from typing import TYPE_CHECKING
import json

from common import find
from bot import bot
from bot.errors import BotNotFoundError, BotValueError

if TYPE_CHECKING:
    from bot import SlashCommandInteraction, SlashAutocompleteInteraction


@bot.slash_command('info')
async def show_info_entry(sci: SlashCommandInteraction, info_entry: str):
    if (entry := find(lambda i: i['entry'] == info_entry, sci.guild.cfg.info_library)) is None:
        raise BotNotFoundError(f"Entry '{info_entry}' is not found in the server info library.")

    content = None if (not entry['content'] or len(entry['content'].strip()) == 0) else entry['content']
    embed = None if (not entry['embed'] or len(entry['embed'].strip()) == 0) else entry['embed']
    if not content and not embed:
        raise BotValueError('Entry does not have any content or embed data.')

    if embed:
        await sci.reply_raw(content=content, embeds=[json.loads(embed)], flags=1 << 6 if entry['ephemeral'] else 0)
    else:
        await sci.reply_raw(content=content, flags=1 << 6 if entry['ephemeral'] else 0)


@bot.slash_autocomplete('info_entry')
async def autocomplete_info_entry(sai: SlashAutocompleteInteraction) -> list[dict]:
    value = sai.value.lower()
    return [
        {'name': i['entry'], 'value': i['entry']}
        for i in sai.guild.cfg.info_library
        if i['entry'].find(value) >= 0
    ][:25]
