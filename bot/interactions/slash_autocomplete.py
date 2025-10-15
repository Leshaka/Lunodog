from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from nextcore.http import Route

from bot import Member

if TYPE_CHECKING:
    from discord_typings import InteractionCreateData

    from bot import Bot


logger = getLogger(__name__)


class SlashAutocompleteInteraction:

    def __init__(self, bot: Bot, interaction_data: InteractionCreateData):
        self.data = interaction_data
        self.author = Member.from_api(self.data['member'])
        self.bot = bot
        self.guild = self.bot.guilds.get(interaction_data['guild_id'])
        option = self.get_autocomplete_option()
        self.option = option['name']
        self.value = option['value']
        self.callback = self.bot.slash_autocompletes.get(self.option)

    def get_autocomplete_option(self) -> dict:
        for option in self.data['data']['options']:
            if option.get('focused') is True:
                return option
            for sub_option in option.get('options', []):
                if sub_option.get('focused') is True:
                    return sub_option

    async def answer(self):
        if self.callback is not None:
            choices: list[dict] = await self.callback(self)
        else:
            # TODO: log 404?
            choices = []

        route = Route(
            "POST",
            "/interactions/{interaction_id}/{interaction_token}/callback",
            interaction_id=self.data['id'],
            interaction_token=self.data['token'],
        )
        await self.guild.bot.http_client.request(
            route,
            rate_limit_key=None,
            json={'type': 8, 'data': {'choices': choices}}
        )
