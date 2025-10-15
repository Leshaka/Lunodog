BOT_OWNER_IDS = ['your-discord-user-id']

DC_BOT_TOKEN = ''
DC_APPLICATION_ID = ''
DC_CLIENT_ID = ''
DC_CLIENT_SECRET = ''
DC_BOT_INTENTS = (
    1 << 0 |  # GUILDS
    1 << 1 |  # GUILD_MEMBERS
    1 << 8 |  # GUILD_PRESENCES
    1 << 9 |  # GUILD_MESSAGES
    1 << 10  # GUILD_MESSAGE_REACTIONS
)
DC_SHARD_COUNT = 1
DC_SHARD_ID = 0

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DB = 'your-db-name'
MYSQL_USER = 'db-user'
MYSQL_PASS = 'db-password'

API_HOST = '127.0.0.1'  # listen on this host (0.0.0.0 for any)
API_PORT = 4300
API_SSL_CERT = 'certs/lunodog.crt'
API_SSL_KEY = 'certs/private.key'
API_OAUTH_SCOPES = ['identify', 'guilds']
API_CORS_ORIGINS = ('http://127.0.0.1:3355',)  # web ui URL
API_OAUTH_REDIRECT_URI = 'http://127.0.0.1:3355/oauth'  # web ui URL/oauth

TWITCH_CLIENT_ID = ''
TWITCH_CLIENT_SECRET = ''
TWITCH_POLL_DELAY = 60

DANBOORU_USERNAME = ''
DANBOORU_API_KEY = ''
