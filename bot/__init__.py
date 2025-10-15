from .objects import DiscordObject, Channel, Thread, Member, FakeMember, MemberPresence, Role
from . import errors
from . import cfg

from .interactions import SlashCommandInteraction, SlashCommandCallback, SlashAutocompleteInteraction
from .guild import Guild
from .client import Bot

bot = Bot()
