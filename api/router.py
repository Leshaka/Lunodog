import logging
from aiohttp import web
import traceback
import json

from bot import bot, Member
from . import ApiServer, oauth, ApiError

logger = logging.getLogger(__name__)


class ApiRoute:
    """
    This class is a decorator for API route functions. It does:
        Register routes with '/api' prefix.
        Prevent calling the function if connection to discord is not ready.
        Provide oauth_user if auth=True is passed.
        Provide discord.Member if get_member=True is passed.
        Restrict Members without guild administrator privileges from using protected routes.
        Provide post json data as kwargs.
        Handle regular (ApiError) exceptions.
        Handle unexpected exceptions.
    """

    def __init__(self, path, method='GET', auth=False, get_member=False, only_admin=False):
        self.path = path
        self.method = method
        self.auth = auth or get_member or only_admin
        self.member = get_member
        self.only_admin = only_admin

    def __call__(self, coro):
        async def decorator(request):
            return await self.wrapper(request, coro)

        logger.info(f"API| registering route /api{self.path}")
        ApiServer.app.router.add_route(self.method, '/api' + self.path, decorator)
        #if self.method == 'POST': # TODO
        #    ApiServer.app.router.add_options('/api' + self.path, decorator)
        return decorator

    # Main function
    async def wrapper(self, request: web.Request, coro):
        # Check if the bot is ready to process api requests.
        if not bot.ready:
            return ApiError(code=503, title="Bot is under connection.",
                            message="Please try again later...").web_response()

        # Prepare kwargs and run the function
        try:
            kwargs = await self.get_post_data(request) if self.method == 'POST' else dict(request.query)

            if self.auth:
                kwargs['oauth_user'] = await self.get_oauth_user(request)

            if self.member or self.only_admin:
                member = await self.fetch_member(
                    oauth_user=kwargs.get('oauth_user'),
                    guild_id=kwargs.get('guild_id')
                )
                if self.only_admin and not member.guild_permissions.administrator:  # TODO
                    raise ApiError(403, 'Missing permissions', 'Must possess guild administrator permissions.')
                if self.member:
                    kwargs['member'] = member
                    kwargs['guild'] = bot.guilds.get(kwargs['guild_id'])
                    kwargs.pop('guild_id')

            logger.info(f"Running {coro.__name__}...")
            return await coro(request, **kwargs)

        # Catch regular exceptions
        except ApiError as e:
            return e.web_response()

        # Catch unexpected exceptions
        except (Exception, BaseException) as e:
            logger.error("\n".join([
                "API request failed with an unexpected exception!",
                f"URL: {request.rel_url}",
                f"Error: {e}",
                f"Traceback: {traceback.format_exc()}"
            ]))
            return ApiError(code=500, title="Internal Server Error", message="Unknown API error.").web_response()

    @staticmethod
    async def get_post_data(request):
        try:
            data = await request.json()
        except json.decoder.JSONDecodeError:
            return ApiError(code=400, title="API error.", message="Bad post data.").web_response()
        else:
            return data

    @staticmethod
    async def get_oauth_user(request) -> dict:
        if (api_token := request.cookies.get('api_token')) is None:
            raise ApiError(401, 'Not authorized', 'api_token is missing.')
        return await oauth.get_user(api_token)

    @staticmethod
    async def fetch_member(oauth_user: dict, guild_id: str = None) -> Member:
        if guild_id is None or not guild_id.isdigit():
            raise ApiError(400, 'Bad request', 'Server parameter is bad or missing.')
        if (guild := bot.guilds.get(guild_id)) is None:
            raise ApiError(400, 'Bad request', f'Server with id {guild_id} is not reachable.')
        if (member := await guild.fetch_member(str(oauth_user['user_id']))) is None:
            raise ApiError(403, 'Missing permissions', 'Must be member of the guild.')
        return member
