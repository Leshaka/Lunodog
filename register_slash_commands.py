from discord_typings import ApplicationCommandPayload
from nextcore.http import BotAuthentication, HTTPClient, Route
import asyncio

from config import DC_BOT_TOKEN, DC_APPLICATION_ID


class CommandType:
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3
    PRIMARY_ENTRY_POINT = 4


class OptionType:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4  # Any integer between -2^53 and 2^53
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7  # Includes all channel types + categories
    ROLE = 8
    MENTIONABLE = 9  # Includes users and roles
    NUMBER = 10  # Any double between -2^53 and 2^53
    ATTACHMENT = 11


SLASH_COMMANDS: list[dict] = [
    {  # modules/info_library
        'name': 'info',
        'description': 'Show an entry from server info library.',
        'options': [
            {
                'type': OptionType.STRING,
                'name': 'info_entry',
                'description': 'Info entry',
                'autocomplete': True,
                'required': True
            }
        ]
    },
    {  # modules/big_emoji
        'name': 'emoji',
        'description': 'Show a server emoji',
        'options': [
            {
                'type': OptionType.STRING,
                'name': 'emoji',
                'description': 'Emoji name',
                'autocomplete': True,
                'required': True
            }
        ]
    },
    {
        'name': 'avatar',
        'description': 'Show a server member avatar',
        'options': [
            {
                'type': OptionType.USER,
                'name': 'user',
                'description': 'User',
                'required': True
            }
        ]
    },
    {  # modules/member_stats
        'name': 'profile',
        'description': 'Show a server member stats profile.',
        'options': [
            {
                'type': OptionType.USER,
                'name': 'user',
                'description': 'User',
                'required': True
            }
        ]
    },
    {  # modules/translator
        "name": "Translate",
        "type": CommandType.MESSAGE
    },
    {  # modules/role_subscriber
        'name': 'role',
        'description': 'Gain or remove server roles.',
        'options': [
            {  # modules/role_subscriber
                'name': 'subscribe',
                'type': OptionType.SUB_COMMAND,
                'description': 'Gain server roles.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'subscription_name',
                        'description': 'Subscription name',
                        'autocomplete': True,
                        'required': True
                    }
                ]
            },
            {  # modules/role_subscriber
                'name': 'unsubscribe',
                'type': OptionType.SUB_COMMAND,
                'description': 'Remove server roles.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'subscription_name',
                        'description': 'Subscription name',
                        'autocomplete': True,
                        'required': True
                    }
                ]
            }
        ]
    },
    {  # modules/qstat
        'name': 'qstat',
        'description': 'Query game servers',
        'options': [
            {
                'name': 'fast',
                'type': OptionType.BOOLEAN,
                'description': 'Do not query master servers',
                'required': False
            }
        ]
    },
    {  # modules/isolator
        'name': 'isolator',
        'description': 'Manage the isolation ward.',
        'options': [
            {
                'name': 'isolate',
                'type': OptionType.SUB_COMMAND,
                'description': 'Isolate a server member.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'user',
                        'description': 'Provide a member mention or user_id:username mask if user is not on the server',
                        'required': True
                    },
                    {
                        'type': OptionType.STRING,
                        'name': 'duration',
                        'description': 'Isolation duration in format 34[m|h|d|W|M|Y] or inf.',
                        'required': True
                    },
                    {
                        'type': OptionType.STRING,
                        'name': 'reason',
                        'description': 'Specify a reason',
                        'required': False
                    },
                ]
            },
            {
                'name': 'release',
                'type': OptionType.SUB_COMMAND,
                'description': 'Release a prisoner from the isolation ward.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'prisoner',
                        'description': 'Prisoner username',
                        'autocomplete': True,
                        'required': True
                    },
                    {
                        'type': OptionType.STRING,
                        'name': 'comment',
                        'description': 'Specify a reason',
                        'required': False
                    }
                ]
            },
            {
                'name': 'mute',
                'type': OptionType.SUB_COMMAND,
                'description': 'Mute a prisoner.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'prisoner',
                        'description': 'Prisoner username',
                        'autocomplete': True,
                        'required': True
                    },
                    {
                        'type': OptionType.STRING,
                        'name': 'comment',
                        'description': 'Specify a reason',
                        'required': False
                    }
                ]
            },
            {
                'name': 'unmute',
                'type': OptionType.SUB_COMMAND,
                'description': 'Unmute a prisoner.',
                'options': [
                    {
                        'type': OptionType.STRING,
                        'name': 'prisoner',
                        'description': 'Prisoner username',
                        'autocomplete': True,
                        'required': True
                    },
                    {
                        'type': OptionType.STRING,
                        'name': 'comment',
                        'description': 'Specify a reason',
                        'required': False
                    }
                ]
            },
            {
                'name': 'list',
                'type': OptionType.SUB_COMMAND,
                'description': 'List the isolation ward.'
            }
        ]
    },
    {  # modules/booru
        'name': 'anime',
        'description': 'Roll a random anime image.',
        'options': [
            {
                'type': OptionType.STRING,
                'name': 'tags',
                'description': 'List of tags',
                'autocomplete': True,
                'required': False
            }
        ]
    },
]


async def register_slash_commands():
    http_client = HTTPClient()
    auth = BotAuthentication(DC_BOT_TOKEN)
    await http_client.setup()

    route = Route("PUT", "/applications/{application_id}/commands", application_id=DC_APPLICATION_ID)
    await http_client.request(
        route, rate_limit_key=auth.rate_limit_key, headers=auth.headers, json=SLASH_COMMANDS
    )
    await http_client.close()
    print('Slash commands registered.')


if __name__ == '__main__':
    asyncio.run(register_slash_commands())

