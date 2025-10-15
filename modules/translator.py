from __future__ import annotations
from typing import TYPE_CHECKING
import aiohttp

from bot import bot, errors

if TYPE_CHECKING:
    from bot import SlashCommandInteraction

TRANSLATE_ROUTE = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={}'


@bot.slash_command('Translate', ephemeral=True, expensive=True)
async def translate_msg(sci: SlashCommandInteraction):
    try:
        msg_text = sci.data['data']['resolved']['messages'].values().__iter__().__next__()['content']
    except (KeyError, StopIteration):
        raise errors.BotValueError('Message content not found.')

    async with aiohttp.ClientSession() as session:
        async with session.get(TRANSLATE_ROUTE.format(msg_text)) as resp:
            data = await resp.json()

    await sci.reply(data[0][0][0])
