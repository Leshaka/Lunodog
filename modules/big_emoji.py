from __future__ import annotations
from typing import TYPE_CHECKING

from common import find
from bot import bot, Member
from bot.errors import BotNotFoundError

if TYPE_CHECKING:
    from bot import SlashCommandInteraction, SlashAutocompleteInteraction


@bot.slash_command('emoji')
async def show_emoji(sci: SlashCommandInteraction, emoji: str):
    emoji = emoji.lower()
    emojis = await sci.bot.api_get_cached(f'/guilds/{sci.guild.id}/emojis')
    if (emoji := find(lambda e: e['name'].lower() == emoji, emojis)) is not None:
        return await sci.reply_raw(embeds=[{"image": {"url": f"https://cdn.discordapp.com/emojis/{emoji['id']}.png"}}])
    raise BotNotFoundError('Specified emoji not found on the server.')


@bot.slash_autocomplete('emoji')
async def autocomplete_emoji(sai: SlashAutocompleteInteraction) -> list[dict]:
    value = sai.value.lower()
    return [
        {'name': i['name'], 'value': i['name']}
        for i in await sai.bot.api_get_cached(f'/guilds/{sai.guild.id}/emojis')
        if i['name'].find(value) >= 0
    ][:25]


@bot.slash_command('avatar')
async def show_avatar(sci: SlashCommandInteraction, user: str):
    target = sci.get_resolved_member(user)
    if not target.avatar:
        raise BotNotFoundError('Not found.')
    await sci.reply_raw(embeds=[{"image": {'url': f'https://cdn.discordapp.com/avatars/{target.id}/{target.avatar}.webp'}}])