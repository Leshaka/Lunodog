import logging

BOT_OWNER_IDS = ['0', 'your-discord-user-id']  # keep '0', it is a system account for API_NO_AUTH=True
BOT_LOGGING_LEVEL = logging.INFO

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
API_PORT = 3355
API_SSL_CERT = None  # set a path to your SSL certificate to enable https
API_SSL_KEY = None  # path to your SSL certificate private key
API_NO_AUTH = False  # if you don't want to set up oauth, grants access to all api routes without auth
API_OAUTH_SCOPES = ['identify', 'guilds']
API_OAUTH_REDIRECT_URI = 'http://127.0.0.1:3356/oauth'  # web ui URL/oauth
API_CORS_ORIGINS = ('http://127.0.0.1:3356',)  # the web ui URL, where api requests will be coming from

TWITCH_CLIENT_ID = ''
TWITCH_CLIENT_SECRET = ''
TWITCH_POLL_DELAY = 60

DANBOORU_USERNAME = ''
DANBOORU_API_KEY = ''
