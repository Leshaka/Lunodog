import uvloop
import asyncio
import logging
import time

from config import BOT_LOGGING_LEVEL
from cli import CLILoggingHandler


def run_here(command: str):
    """ This is for CLI to share this module's vars """
    return eval(command)

# Have to initialize logger before importing modules if we want logging on start-up (registered commands, etc)
cli = CLILoggingHandler(runner=run_here)
logging.basicConfig(level=BOT_LOGGING_LEVEL, handlers=[cli])

from bot import bot
from db import db
import modules
import api


# Background processes loop
async def think():
    while bot.running:
        frame_time = time.time()
        await bot.think(frame_time)
        await asyncio.sleep(1)


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    loop.run_until_complete(db.connect(loop=loop))
    loop.run_until_complete(api.ApiServer.start())

    loop.create_task(bot.serve())
    loop.create_task(think())
    task = loop.create_task(cli.serve_cli(loop=loop))
    try:
        loop.run_until_complete(asyncio.wait_for(task, timeout=None))
    except KeyboardInterrupt:
        logging.info('Keyboard interrupt received. Exiting...')
        loop.run_until_complete(bot.close())
        loop.run_until_complete(api.ApiServer.runner.cleanup())
        print('Can exit now.')


if __name__ == '__main__':
    main()
