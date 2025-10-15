from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger

from bot import Guild, SlashCommandInteraction, SlashAutocompleteInteraction

if TYPE_CHECKING:
    import discord_typings as dt
    from . import Bot

logger = getLogger(__name__)


class BotEvents:

    def __init__(self, bot: Bot):
        self.bot = bot
        self.register_events()

    def register_events(self):
        self.bot.event_dispatcher.add_listener(self._on_ready, 'READY')
        self.bot.event_dispatcher.add_listener(self._on_resume, 'RESUMED')
        self.bot.event_dispatcher.add_listener(self._on_guild_create, 'GUILD_CREATE')
        self.bot.event_dispatcher.add_listener(self._on_guild_update, 'GUILD_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_guild_delete, 'GUILD_DELETE')
        self.bot.event_dispatcher.add_listener(self._on_channel_create, 'CHANNEL_CREATE')
        self.bot.event_dispatcher.add_listener(self._on_channel_update, 'CHANNEL_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_channel_delete, 'CHANNEL_DELETE')
        self.bot.event_dispatcher.add_listener(self._on_guild_emojis_update, 'GUILD_EMOJIS_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_member_add, 'GUILD_MEMBER_ADD')
        self.bot.event_dispatcher.add_listener(self._on_member_update, 'GUILD_MEMBER_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_member_remove, 'GUILD_MEMBER_REMOVE')
        self.bot.event_dispatcher.add_listener(self._on_role_create, 'GUILD_ROLE_CREATE')
        self.bot.event_dispatcher.add_listener(self._on_role_update, 'GUILD_ROLE_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_role_delete, 'GUILD_ROLE_DELETE')
        self.bot.event_dispatcher.add_listener(self._on_presence_update, 'PRESENCE_UPDATE')
        self.bot.event_dispatcher.add_listener(self._on_interaction_create, 'INTERACTION_CREATE')
        self.bot.event_dispatcher.add_listener(self._on_message_create, 'MESSAGE_CREATE')
        self.bot.event_dispatcher.add_listener(self._on_shard_disconnect, 'shard_disconnect')

    async def _on_ready(self, data: dt.ReadyData):
        logger.info(f"Logged in as {data['user']['username']} ({data['user']['id']}).")
        self.bot.unavailable_guilds = [i['id'] for i in data['guilds']]
        if len(self.bot.unavailable_guilds):
            logger.info(f'Waiting for Guild data... {len(self.bot.unavailable_guilds)} left')
            self.bot.ready = False
        else:
            self.bot.first_ready = False
            self.bot.ready = True

    async def _on_resume(self, d: dict):
        logger.info(f'Connection was resumed.')
        self.bot.ready = True

    async def _on_guild_create(self, data: dt.GuildCreateData):
        #  This function is called every time a guild becomes available (usually before READY event)
        logger.debug(f"Create guild for {data['id']}")
        if data['id'] not in self.bot.guilds.keys():
            logger.debug(f'not found in keys: {self.bot.guilds.keys()}')
            self.bot.guilds[data['id']] = await Guild.new(self.bot, data)
        else:
            self.bot.guilds[data['id']].update_self(data)

        # We receive READY event first,
        # and then we have to track all Guilds data are received before the bot can load state and be ready to operate
        if not self.bot.ready:
            if data['id'] in self.bot.unavailable_guilds:
                self.bot.unavailable_guilds.remove(data['id'])
            else:
                logger.warning(f"Unexpected guild create even received @ guild_id {data['id']}")

            if not len(self.bot.unavailable_guilds):
                if self.bot.first_ready:
                    self.bot.first_ready = False
#                    await self.bot.load_state()

            self.bot.ready = True
            logger.info('All Guilds loaded, ready to operate.')

    async def _on_guild_update(self, data: dt.GuildUpdateData):
        #  Data is the same as GUILD_CREATE but without members and channels data
        self.bot.guilds[data['id']].update_self(data)

    async def _on_guild_delete(self, data: dt.GuildDeleteData):
        if data['unavailable']:
            logger.warning(f"Guild with id {data['id']} is unavailable due to an outage.")
        self.bot.guilds.pop(data['id'])

    async def _on_channel_create(self, data: dt.ChannelCreateData):
        self.bot.guilds[data['guild_id']].update_or_create_channel(data)

    async def _on_channel_update(self, data: dt.ChannelUpdateData):
        self.bot.guilds[data['guild_id']].update_or_create_channel(data)

    async def _on_channel_delete(self, data: dt.ChannelUpdateData):
        self.bot.guilds[data['guild_id']].delete_channel(data['id'])

    async def _on_thread_create(self, data: dt.ThreadCreateData):
        self.bot.guilds[data['guild_id']].update_or_create_thread(data)

    async def _on_guild_emojis_update(self, data: dt.GuildEmojisUpdateData):
        self.bot.guilds[data['guild_id']].update_emojis(data['emojis'])

    async def _on_member_add(self, data: dt.GuildMemberAddData):
        self.bot.guilds[data['guild_id']].update_or_create_member(data)

    async def _on_member_update(self, data: dt.GuildMemberUpdateData):
        self.bot.guilds[data['guild_id']].update_or_create_member(data)

    async def _on_member_remove(self, data: dt.GuildMemberRemoveData):
        self.bot.guilds[data['guild_id']].delete_member(data['user']['id'])

    async def _on_role_create(self, data: dt.GuildRoleCreateData):
        self.bot.guilds[data['guild_id']].update_or_create_role(data['role'])

    async def _on_role_update(self, data: dt.GuildRoleUpdateData):
        self.bot.guilds[data['guild_id']].update_or_create_role(data['role'])

    async def _on_role_delete(self, data: dt.GuildRoleDeleteData):
        self.bot.guilds[data['guild_id']].delete_role(data['role_id'])

    async def _on_presence_update(self, data: dt.PresenceUpdateData):
        await self.bot.guilds[data['guild_id']].update_member_presence(data)

    async def _on_interaction_create(self, data: dt.InteractionCreateData):
        if data['type'] == 2:  # it's a /slash command
            sci = SlashCommandInteraction(bot=self.bot, interaction_data=data)
            await sci.run()
            return

        if data['type'] == 3:  # it's a message component (button)
#            bc = ButtonCommand(interaction_data=data, guild=self.bot.guilds[data['guild_id']])
#            await bc.run()
            return

        if data['type'] == 4:  # it's a /slash command autocomplete
            sai = SlashAutocompleteInteraction(bot=self.bot, interaction_data=data)
            await sai.answer()
            return

    async def _on_message_create(self, message: dt.MessageData):
        logger.debug(message)
        # It's an ephemeral (or direct?) message
        if (guild_id := message.get('guild_id')) is None:
            # TODO: answer DM
            return

        # Maybe this can happen in the process of bot being connected
        if (guild := self.bot.guilds.get(guild_id)) is None:
            logger.error(f'Received MESSAGE_CREATE with an unknown guild_id: {guild_id}.')
            return

    async def _on_shard_disconnect(self, code: int | bool):
        # This means shard is disconnected by local request (ShardManager.close() or .rescale_shards())
        if code is True:
            return

        logger.error('A shard closed connection: ' + ('heartbeat timeout.' if code is False else f"code {code}."))
        num_connected_shards = len([shard for shard in self.bot.shard_manager.active_shards if shard.connected.is_set()])
        if num_connected_shards == 0:
            logger.error('No more connected shards left. Bot is no longer ready.')
            self.bot.ready = False
            return
        logger.error(f'{num_connected_shards} connected shards left.')

