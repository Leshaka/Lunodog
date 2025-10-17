from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from nextcore.http.errors import ForbiddenError

from bot import bot
from bot import errors
from common import Colors

if TYPE_CHECKING:
    from discord_typings import MessageReactionAddData, MessageReactionRemoveData
    from bot import SlashCommandInteraction, SlashAutocompleteInteraction

logger = getLogger(__name__)


@bot.event_dispatcher.listen('MESSAGE_REACTION_ADD')
async def on_reaction_add(data: MessageReactionAddData):  # skip DMs
    if (guild := bot.guilds.get(data.get('guild_id'))) is None:
        return
    if not guild.cfg.rs_enable:  # skip if module turned off
        return
    if (member := guild.members.get(data['user_id'])) is None:
        logger.error(f"Guild member is not found for MESSAGE_REACTION_ADD: {guild.id} {data['user_id']}")
        return

    roles_to_add = set((
        row['role'] for row in guild.cfg.rs_emojis
        if (
            row['message_id'] == data['message_id'] and
            row['emoji'] == data['emoji']['name'] and
            row['role'] not in member.roles and
            row['role'] in guild.roles
        )
    ))

    for role_id in roles_to_add:
        logger.debug(f'Adding role {role_id} to member {member}.')
        try:
            await bot.api_put(f"/guilds/{guild.id}/members/{member.id}/roles/{role_id}", data={})
        except ForbiddenError as e:
            logger.error(f'Missing permissions to add role {role_id} to {member.id}: {e}')


@bot.event_dispatcher.listen('MESSAGE_REACTION_REMOVE')
async def on_reaction_remove(data: MessageReactionRemoveData):
    if (guild := bot.guilds.get(data.get('guild_id'))) is None:  # skip DMs
        return
    if not guild.cfg.rs_enable:  # skip if module turned off
        return
    if (member := guild.members.get(data['user_id'])) is None:
        logger.error(f"Guild member is not found for MESSAGE_REACTION_ADD: {guild.id} {data['user_id']}")
        return

    roles_to_remove = set((
        row['role'] for row in guild.cfg.rs_emojis
        if (
            row['message_id'] == data['message_id'] and
            row['emoji'] == data['emoji']['name'] and
            row['role'] in member.roles and
            row['role'] in guild.roles  # just in case
        )
    ))

    for role_id in roles_to_remove:
        logger.debug(f'Removing role {role_id} from member {member}.')
        try:
            await bot.api_delete(f"/guilds/{guild.id}/members/{member.id}/roles/{role_id}")
        except ForbiddenError as e:
            logger.error(f'Missing permissions to remove role {role_id} from {member.id}: {e}')


@bot.slash_command('role subscribe', ephemeral=True)
async def subscribe_role(sci: SlashCommandInteraction, subscription_name: str):
    if not sci.guild.cfg.rs_enable:  # skip if module turned off
        raise errors.BotPermissionError('Role subscriber is disabled on this server.')

    roles_to_add = set((
        row['role'] for row in sci.guild.cfg.rs_commands
        if (
            row['name'] == subscription_name and
            row['allow_sub'] and
            row['role'] not in sci.author.roles and
            row['role'] in sci.guild.roles
        )
    ))
    if not len(roles_to_add):
        raise errors.BotValueError('No roles to add.')
    for role_id in roles_to_add:
        await bot.api_put(f"/guilds/{sci.guild.id}/members/{sci.author.id}/roles/{role_id}", data={})
    await sci.reply(f'Added `{len(roles_to_add)}` roles.', color=Colors.GREEN)


@bot.slash_command('role unsubscribe', ephemeral=True)
async def unsubscribe_role(sci: SlashCommandInteraction, subscription_name: str):
    if not sci.guild.cfg.rs_enable:  # skip if module turned off
        raise errors.BotPermissionError('Role subscriber is disabled on this server.')

    roles_to_remove = set((
        row['role'] for row in sci.guild.cfg.rs_commands
        if (
            row['name'] == subscription_name and
            row['allow_unsub'] and
            row['role'] in sci.author.roles and
            row['role'] in sci.guild.roles
        )
    ))
    if not len(roles_to_remove):
        raise errors.BotValueError('No roles to remove.')
    for role_id in roles_to_remove:
        await bot.api_delete(f"/guilds/{sci.guild.id}/members/{sci.author.id}/roles/{role_id}")
    await sci.reply(f'Removed `{len(roles_to_remove)}` roles.', color=Colors.GREEN)


@bot.slash_autocomplete('subscription_name')
async def autocomplete_subscription(sai: SlashAutocompleteInteraction) -> list[dict]:
    """ Return only options what will change author roles """

    if sai.data['data']['options'][0]['name'] == 'unsubscribe':
        available_subscriptions = set((
            row['name']
            for row in sai.guild.cfg.rs_commands
            if row['name'].find(sai.value) >= 0 and row['allow_unsub'] and row['role'] in sai.author.roles
        ))
    else:
        available_subscriptions = set((
            row['name']
            for row in sai.guild.cfg.rs_commands
            if row['name'].find(sai.value) >= 0 and row['allow_sub'] and row['role'] not in sai.author.roles
        ))
    return [{'name': i, 'value': i} for i in available_subscriptions][:25]
