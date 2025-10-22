# -*- coding: utf-8 -*-
import logging
import ssl
from aiohttp_middlewares import cors_middleware
from aiohttp_middlewares.cors import DEFAULT_ALLOW_HEADERS
from aiohttp import web

import config


logger = logging.getLogger(__name__)


class ApiServer:

    app = web.Application(
        middlewares=[cors_middleware(origins=config.API_CORS_ORIGINS, allow_credentials=True, allow_headers=DEFAULT_ALLOW_HEADERS + ("X-Client-UID",), allow_methods=("GET", "POST", "PATCH", "OPTIONS", "HEAD"))]
    )
    runner = web.AppRunner(app)
    context = None
    if config.API_SSL_CERT:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(
            certfile=config.API_SSL_CERT,
            keyfile=config.API_SSL_KEY
        )

    @classmethod
    async def start(cls):
        await cls.runner.setup()
        site = web.TCPSite(cls.runner, config.API_HOST, config.API_PORT, ssl_context=cls.context)
        await site.start()
        logger.info(f'API| Serving at https://{config.API_HOST}:{config.API_PORT}')
