from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from nextcore.http.errors import NotFoundError

from config import BOT_OWNER_IDS
from bot import DiscordObject, Channel, Thread, Role, Member, MemberPresence
from bot.cfg import Config, StrVar, RoleVar, IntVar, ListVar, BoolVar, TextChannelVar

if TYPE_CHECKING:
    from discord_typings import GuildCreateData, GuildUpdateData, PresenceUpdateData

    from bot import Bot

logger = getLogger(__name__)


class GuildConfig(Config):
    _table_name = 'guild_config'
    _name = 'guild_config'
    _variables = dict(
        admin_role=RoleVar(),
        moderator_role=RoleVar(),
        info_library=ListVar(
            variables=dict(
                entry=StrVar(notnull=True, min_length=1, max_length=64),
                content=StrVar(notnull=False, max_length=2048),
                embed=StrVar(notnull=False, max_length=2048),
                ephemeral=BoolVar(default=False)
            ),
        ),
        greetings_enable=BoolVar(default=False, notnull=True),
        greetings_welcome_channel=TextChannelVar(),
        greetings_welcome_message=StrVar(),
        greetings_welcome_back_message=StrVar(),
        greetings_goodbye_channel=TextChannelVar(),
        greetings_goodbye_message=StrVar(),
        greetings_goodbye_again_message=StrVar(),
        rs_enable=BoolVar(default=False),  # role subscriber
        rs_emojis=ListVar(
            variables=dict(
                message_id=StrVar(notnull=True),
                emoji=StrVar(notnull=True),
                role=RoleVar(),
                comment=StrVar()
            ),
        ),
        rs_commands=ListVar(
            variables=dict(
                name=StrVar(notnull=True),
                role=RoleVar(),
                allow_sub=BoolVar(),
                allow_unsub=BoolVar(),
                comment=StrVar()
            ),
        ),
        qstat_enable=BoolVar(default=False),
        qstat_string=StrVar(),
        qstat_show_empty=BoolVar(default=False),
        qstat_show_full=BoolVar(default=True),
        qstat_sortby=StrVar(default='numclients', notnull=True),
        qstat_filter=StrVar(default='{"gamename": "cpma"}'),
        qstat_master_servers=ListVar(
            variables=dict(
                host=StrVar(notnull=True),
                port=IntVar(notnull=True),
                game_protocol=StrVar(notnull=True),
                comment=StrVar()
            )
        ),
        qstat_servers=ListVar(
            variables=dict(
                host=StrVar(notnull=True),
                port=IntVar(notnull=True),
                flag=StrVar(),
                comment=StrVar()
            )
        ),
        isolator_role=RoleVar(),
        isolator_mute_role=RoleVar(),
        isolator_log_channel=TextChannelVar(),
        twitch_enable=BoolVar(default=False),
        twitch_announcement_channel=TextChannelVar(),
        twitch_summary=BoolVar(default=True),
        twitch_channels=ListVar(
            variables=dict(
                channel=StrVar(notnull=True),
                allowed_games=StrVar(default="*", notnull=True),
                message_text=StrVar()
            )
        ),
        yt_enable=BoolVar(default=False),
        yt_announcement_channel=TextChannelVar(),
        yt_channels=ListVar(
            variables=dict(
                channel=StrVar(notnull=True),
                post_videos=BoolVar(default=True),  # Toggle to announce broadcasts
                post_shorts=BoolVar(default=True),
                post_broadcasts=BoolVar(default=True)  # Toggle to announce broadcasts
            )
        )
    )

    admin_role: int | None
    moderator_role: int | None
    greetings_enable: bool
    greetings_welcome_channel: int | None
    greetings_welcome_message: str | None
    greetings_welcome_back_message: str | None
    greetings_goodbye_channel: int | None
    greetings_goodbye_message: str | None
    greetings_goodbye_again_message: str | None
    rs_enable: bool | None
    rs_emojis: list[dict]
    rs_commands: list[dict]
    isolator_role: int | None
    isolator_mute_role: int | None
    isolator_log_channel: int | None
    qstat_enable: bool
    qstat_string: str
    qstat_show_empty: bool
    qstat_show_full: bool
    qstat_filter: str | None
    qstat_master_servers: list
    qstat_servers: list
    isolator_role: int | None
    isolator_mute_role: int | None
    isolator_log_channel: int | None
    twitch_enable: bool
    twitch_announcement_channel: int | None
    twitch_summary: bool
    twitch_channels: list[dict]
    yt_enable: bool
    yt_announcement_channel: int | None
    yt_channels: list[dict]


class Guild(DiscordObject):
    _fields = ['id', 'name', 'owner_id', 'icon']

    def __init__(self, bot: Bot, guild_data: GuildCreateData, cfg: GuildConfig):
        self.cfg = cfg
        self.bot = bot
        self.id = guild_data['id']
        self.name = guild_data['name']
        self.owner_id = guild_data['owner_id']
        self.icon = guild_data['icon']

        self.roles: dict[str, Role] = {i['id']: Role(i) for i in guild_data['roles']}

        self.members: dict[str, Member] = {i['user']['id']: Member.from_api(i) for i in guild_data['members']}
        self.presences: dict[str, MemberPresence] = {i['user']['id']: MemberPresence.from_api(i) for i in guild_data['presences']}
        # if a guild is large, presences do not contain offline/invisible members
        for user_id in self.members:
            if user_id not in self.presences:
                self.presences[user_id] = MemberPresence(status='offline')

        self.admin_roles: set[str] = {i.id for i in self.roles.values() if int(i.permissions) & (1 << 3)}
        self.channels: dict[str, Channel] = {i['id']: Channel(i) for i in guild_data['channels']}
        self.threads: dict[str, Thread] = {i['id']: Thread(i) for i in guild_data['threads']}

    def __repr__(self):
        return f'<Guild {self.name} id={self.id}>'

    @classmethod
    async def new(cls, bot: Bot, guild_data: GuildCreateData) -> Guild:
        logger.debug(f'Creating guild {guild_data["name"]}...')
        guild = cls(
            bot=bot,
            guild_data=guild_data,
            cfg=await GuildConfig.get_or_create(p_key=int(guild_data['id'])),
        )

        return guild

    def update_self(self, guild_data: GuildUpdateData):
        logger.debug(f'Updating guild {guild_data["name"]}...')
        self.id = guild_data['id']
        self.name = guild_data['name']
        self.owner_id = guild_data['owner_id']
        self.icon = guild_data['icon']

        for role_data in guild_data['roles']:
            self.update_or_create_role(role_data)

    def update_or_create_channel(self, channel_data: dict):
        if (channel := self.channels.get(channel_data['id'])) is not None:
            channel.update(channel_data)
            return
        self.channels[channel_data['id']] = Channel(channel_data)

    def update_or_create_thread(self, thread_data: dict):
        if (thread := self.threads.get(thread_data['id'])) is not None:
            thread.update(thread_data)
            return
        self.threads[thread_data['id']] = Thread(thread_data)

    def update_or_create_member(self, member_data: dict):
        if (member := self.members.get(member_data['user']['id'])) is not None:
            member.update(member_data)
            return
        self.members[member_data['user']['id']] = Member.from_api(member_data)

    def update_or_create_role(self, role_data: dict):
        if int(role_data['permissions']) & (1 << 3):
            self.admin_roles.add(role_data['id'])
        else:
            self.admin_roles.discard(role_data['id'])

        if (role := self.roles.get(role_data['id'])) is not None:
            role.update(role_data)
            return
        self.roles[role_data['id']] = Role(role_data)

    def delete_role(self, role_id: str):
        self.admin_roles.discard(role_id)
        for m in filter(lambda i: role_id in i.roles, self.members.values()):
            m.roles.remove(role_id)
        self.roles.pop(role_id)

    def delete_channel(self, channel_id: str):
        self.channels.pop(channel_id)

    def delete_member(self, member_id: str):
        if member_id in self.members:
            self.members.pop(member_id)
        if member_id in self.presences:
            self.presences.pop(member_id)

    async def update_member_presence(self, presence_data: PresenceUpdateData):
        old_presence = self.presences.get(presence_data['user']['id'])  # should only be None if it's a new Member
        self.presences[presence_data['user']['id']] = MemberPresence.from_api(presence_data)
        if old_presence:
            await self.bot.event_dispatcher.dispatch(
                'BOT_MEMBER_PRESENCE_CHANGE',
                old_presence,  # old presence
                presence_data  # new presence
            )

    def is_admin(self, member: Member) -> bool:
        if any((
                role_id == self.cfg.admin_role or role_id in self.admin_roles
                for role_id in member.roles
        )) or member.id == self.owner_id or member.id in BOT_OWNER_IDS:
            return True
        return False

    async def fetch_member(self, user_id: str) -> Member | None:
        """ Get existing from self.members or fetch from discord API and save to self.members """
        if (member := self.members.get(user_id)) is not None:
            return member
        try:
            self.members[user_id] = Member.from_api(await self.bot.api_get(f'/guilds/{self.id}/members/{user_id}'))
            return self.members[user_id]
        except NotFoundError:
            return None
