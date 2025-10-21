from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
import traceback
import time
from asyncio import wait_for, shield
from nextcore.http import Route
from nextcore.http.errors import HTTPRequestStatusError, ForbiddenError
from aiohttp.http_exceptions import HttpProcessingError

from bot import errors, Member
from common import Colors

if TYPE_CHECKING:
    from typing import Callable
    from discord_typings import InteractionCreateData, MessageData

    from bot import Bot

logger = getLogger(__name__)


class SlashCommandCallback:

    def __init__(self, func: Callable, ephemeral: bool = False, expensive: bool = False):
        self.func = func
        self.ephemeral = ephemeral
        self.expensive = expensive


class SlashCommandInteraction:

    def __init__(self, bot: Bot, interaction_data: InteractionCreateData):
        # TODO: self.guild could be None on connect, same for autocomplete
        self.bot = bot
        self.data = interaction_data
        self.guild = self.bot.guilds.get(interaction_data['guild_id'])
        self.name, self.options = self.parse_slash_command_options()
        self.is_answered = False
        self.channel = self.guild.channels.get(self.data['channel_id'])
        self.author = Member.from_api(self.data['member'])
        self.callback = self.bot.slash_commands.get(self.name)

    def get_resolved_member(self, user_id: str) -> Member:
        m_data = self.data['data']['resolved']['members'][user_id]
        m_data['user'] = self.data['data']['resolved']['users'][user_id]
        return Member.from_api(m_data)

    def parse_slash_command_options(self) -> tuple[str, dict]:
        """ Parse slash command interaction options return full command name and options as kwargs """
        cmd_name = self.data['data']['name']
        kwargs = {}

        for option in self.data['data'].get('options', []):
            if option['type'] == 1:
                cmd_name += ' ' + option['name']
                for sub_option in option.get('options', []):
                    kwargs[sub_option['name']] = sub_option['value']
                break  # /slash command can only have one subcommand option
            kwargs[option['name']] = option['value']
        return cmd_name, kwargs

    async def run(self):
        if self.callback is None:
            logger.error(f'Recieved unknown slash command `/{self.name}`.')
            return

        logger.debug(f'Running slash command /{self.name} {self.options}')
        if self.callback.expensive:
            await self._run_expensive_callback()
        else:
            await self._run_callback()

    async def _run_expensive_callback(self):
        """ Wait 2 seconds for the callback to complete, send ACK (defer response) if not completed in time """
        # get passed time since interaction was created, convert snowflake into timestamp
        passed_time = time.time() - (((int(self.data['id']) >> 22) + 1420070400000) / 1000.0)

        if passed_time >= 3.0:  # Interactions must be answered within 3 seconds or they time out
            logger.error('Skipping outdated interaction.')
            return

        try:
            await wait_for(shield(self._run_callback()), timeout=max(2.5-passed_time, 0))
        except TimeoutError:
            logger.warning('Deferring /slash command')
            await self.send_response({'flags': 1 << 6 if self.callback.ephemeral else 0}, response_type=5)

    async def _run_callback(self):
        try:
            await self.callback.func(self, **self.options)
        except errors.BotException as e:
            await self.reply(str(e), color=Colors.RED)
        except ForbiddenError as e:
            #  TODO: inform guild owner of incorrect permissions
            await self.reply(f"Received **ForbiddenError** from Discord API. Review bot's server permissions.", color=Colors.RED)
            self.log_exc(e, self.callback.func, self.options)
        except (HTTPRequestStatusError, HttpProcessingError) as e:
            # once we send an invalid response we cant re-respond and inform user about the exception anymore
            self.log_exc(e, self.callback.func, self.options)
        except Exception as e:
            await self.reply(f'RuntimeError: {str(e)}', color=Colors.RED)
            self.log_exc(e, self.callback.func, self.options)

    async def reply(self, content: str, color: int = Colors.DARK, mention: bool = False):
        await self.send_response(data={
            "flags": 1 << 6 if self.callback.ephemeral else 0,
            "embeds": [{"type": 4, "color": color, "description": content}]
        })

    async def reply_raw(self, **data: MessageData):
        await self.send_response(data=data)

    def log_exc(self, e: Exception, callback: Callable, kwargs):
        logger.error("\n".join([
            f'Error processing /slash command {callback.__name__}.',
            f'Guild: {self.guild.name} ({self.guild.id})',
            f'Member: {self.author.display_name} ({self.author.id}).',
            f'Kwargs: {kwargs}.',
            f'Exception: {str(e)}. Traceback:\n{traceback.format_exc()}=========='
        ]))

    async def send_response(self, data: MessageData, response_type=4):
        if self.is_answered:
            logger.warning('Sending follow-up.')
            await self.send_followup(data)
            return

        self.is_answered = True
        logger.warning('Is answered is now TRUE')
        route = Route(
            "POST",
            "/interactions/{interaction_id}/{interaction_token}/callback",
            interaction_id=self.data["id"],
            interaction_token=self.data["token"],
        )
        await self.bot.http_client.request(route, rate_limit_key=None, json={'type': response_type, 'data': data})

    async def send_followup(self, data: MessageData):
        route = Route(
            "POST",
            "/webhooks/{application_id}/{interaction_token}",
            application_id=self.data['application_id'],
            interaction_token=self.data['token']
        )
        await self.bot.http_client.request(route, rate_limit_key=None, json=data)
