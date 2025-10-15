from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger
from time import time

if TYPE_CHECKING:
    from discord_typings import ChannelData, ThreadChannelData, GuildMemberData, RoleData, PresenceUpdateData

    from bot import Guild

logger = getLogger(__name__)


class DiscordObject:
    _fields = []

    def json(self) -> dict:
        return {
            field: self.__getattribute__(field)
            for field in self._fields
        }


class Channel(DiscordObject):
    _fields = ['id', 'type', 'name']

    def __init__(self, data: ChannelData):
        self.id: str = data['id']
        self.type: int = data['type']
        self.name: str = data['name']

    def __repr__(self):
        return f'<Channel {self.name} type={self.type} id={self.id}>'

    def update(self, data: ChannelData):
        self.type = data['type']
        self.name = data['name']


class Thread(DiscordObject):
    _fields = ['id', 'name', 'archived']

    def __init__(self, data: ThreadChannelData):
        self.id = data['id']
        self.name = data['name']
        self.type = data['type']
        self.archived = data['thread_metadata']['archived']

    def update(self, data: ThreadChannelData):
        self.name = data['name']
        self.archived = data['thread_metadata']['archived']


class Member(DiscordObject):
    _fields = ['id', 'username', 'global_name', 'bot', 'display_name', 'roles', 'avatar', 'fake']

    def __init__(
            self, user_id: str, username: str, global_name: str, bot: bool, nick: str | None, avatar: str | None,
            fake: bool, roles: list[str]
    ):
        self.id = user_id
        self.username = username
        self.global_name = global_name
        self.bot = bot
        self.display_name = nick or self.global_name or self.username
        self.avatar = avatar
        self.fake = fake
        self.roles = roles
        self.status = None  # Unfortunately this is not provided with Member or User data

    def __repr__(self):
        return f'<Member {self.username} id={self.id}>'

    def mention(self):
        return f'<@{self.id}>'

    @classmethod
    def from_api(cls, data: GuildMemberData):
        return cls(
            user_id=data['user']['id'],
            username=data['user']['username'],
            global_name=data['user']['global_name'],
            bot=data['user'].get('bot') or False,
            nick=data['nick'],
            avatar=data['avatar'] or data['user']['avatar'],
            fake=False,
            roles=data['roles'],
        )

    @classmethod
    def from_state(cls, guild: Guild, data: dict) -> Member:
        """ Returns existing Member object or creates FakeMember """
        if data['fake']:
            return FakeMember(**data)
        elif (member := guild.members.get(data['user_id'])) is None:
            # Maybe raise error instead?
            logger.warning(f'Creating non-existing member @ {guild}: {data}')
            return FakeMember(**data)
        return member

    def serialize(self) -> dict:
        return dict(user_id=self.id, username=self.username, fake=self.fake)

    def update(self, data: dict):
        self.username = data['user']['username']
        self.global_name = data['user']['global_name']
        self.display_name = data['nick'] or self.display_name
        self.roles = data['roles']

    def set_status(self, status: str):
        self.status = status

    def __eq__(self, other):
        return self.id == other.id


class MemberPresence(DiscordObject):
    _fields = ['status', 'at']

    def __init__(self, status: str):
        self.status = status
        self.at = int(time())

    @classmethod
    def from_api(cls, data: PresenceUpdateData):
        return cls(
            status=data['status']
        )


class FakeMember(Member):
    """ Represents unreachable or completely fake Member """

    def __init__(self, user_id: str, username: str):
        super().__init__(
            user_id=user_id, username=username, global_name=username, bot=False, nick=None, avatar=None,
            fake=True, roles=[]
        )

    def __repr__(self):
        return f'<FakeMember {self.username} id={self.id}>'

    def mention(self):
        return f'<{self.username}@{self.id}>'


class Role(DiscordObject):
    _fields = ['id', 'name', 'permissions']

    def __init__(self, data: RoleData):
        self.id = data['id']
        self.name = data['name']
        self.permissions = data['permissions']

    def __repr__(self):
        return f'<Role {self.name} id={self.id}>'

    def update(self, data: RoleData):
        self.name = data['name']
        self.permissions = data['permissions']
