from logging import getLogger
from aiohttp.web import Request

from config import BOT_OWNER_IDS
from bot import bot, Guild, Member
from . import ApiRoute, ApiError, api_success, oauth

logger = getLogger(__name__)


# Client should get redirected to this route from discord oauth url like:
# https://discord.com/api/oauth2/authorize?
#   client_id={DC_CLIENT_ID}&redirect_uri={API_OAUTH_REDIRECT_URI}&response_type=code&scope={' '.join(API_OAUTH_SCOPES)}
# But in this case client gets redirected to the vuejs oauth page, that passes the url query to this route as post
@ApiRoute('/oauth', method='POST', auth=False)
async def do_oauth(request: Request, code=None):
    if code is None:
        raise ApiError(code=400, title='Bad Request', message='Oauth2 code is missing in the request.')

    oauth_user = await oauth.do_oauth(code)
    response = api_success()
    response.set_cookie('api_token', oauth_user['api_token'], samesite=None, secure=True)
    return response


@ApiRoute('/me', method='GET', auth=True)
async def get_me(request: Request, oauth_user: dict):
    return api_success({
        'user_id': str(oauth_user['user_id']),
        'username': oauth_user['username'],
        'avatar': oauth_user['avatar']
    })


@ApiRoute('/me/guilds', method='GET', auth=True)
async def get_my_guilds(request: Request, oauth_user: dict):
    # Return all guilds for bot owners
    if str(oauth_user['user_id']) in BOT_OWNER_IDS:
        return api_success([{
            'id': str(g.id),
            'icon': g.icon,
            'name': g.name,
            'is_admin': True
        } for g in bot.guilds.values()])

    # Return only guilds the user is member of
    guilds = []
    for g in bot.guilds.values():
        if (m := g.members.get(str(oauth_user['user_id']))) is None:
            continue
        guilds.append({
            'id': str(g.id),
            'icon': g.icon,
            'name': g.name,
            'is_admin': g.is_admin(m)
        })
    return api_success(guilds)


@ApiRoute('/config/get', method='GET', get_member=True)
async def get_guild_config(request: Request, oauth_user: dict, guild: Guild, member: Member):
    if not guild.is_admin(member):
        raise ApiError(code=403, message="You are missing privileges to edit the configuration.")

    return api_success({
        'id': str(guild.id),
        'icon': guild.icon,
        'name': guild.name,
        'is_admin': guild.is_admin(member),
        'text_channels': [{'name': c.name, 'id': c.id} for c in guild.channels.values() if c.type == 0],
        'roles': [{'name': r.name, 'id': r.id} for r in guild.roles.values()],
        'config': guild.cfg.__dict__()
    })


@ApiRoute('/config/update', method='POST', get_member=True)
async def update_guild_config(request: Request, oauth_user: dict, guild: Guild, member: Member, cfg: dict):
    if not guild.is_admin(member):
        raise ApiError(code=403, message="You are missing privileges to edit the configuration.")

    errors = guild.cfg.validate(guild, cfg)
    if len(errors):
        message = 'Bad values for variables:\n'
        message += '\n'.join((f'\t{var}\n\t\t{error}' for var, error in errors.items()))
        raise ApiError(code=400, title='Incorrect config values', message=message)
    await guild.cfg.update(cfg)
    return api_success()


@ApiRoute('/logout', method='GET', auth=True)
async def logout(request: Request, oauth_user: dict):
    await oauth.delete_user(oauth_user)
    r = api_success()
    r.del_cookie('api_token')
    return r


@ApiRoute('/test_authed', method='GET', auth=True)
async def test_authed(request: Request, oauth_user: dict):
    return api_success({'success': f"You are authed as {oauth_user['username']}"})


@ApiRoute('/test', method='GET')
async def test(request: Request):
    return api_success({'content': 'hello world'})
