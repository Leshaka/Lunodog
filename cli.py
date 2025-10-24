from __future__ import annotations
import sys
import asyncio
import logging
import readline
import rlcompleter  # this does python autocomplete by tab

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop
    from typing import Any, TYPE_CHECKING


class CLILoggingHandler(logging.Handler):

    def __init__(self, *args, runner=eval, **kwargs):
        super().__init__(*args, **kwargs)
        self.runner = runner
        # Go down to bottom of the terminal, this allows to restore cursor position without issues
        sys.stdout.write('\033[1000B')

    async def serve_cli(self, loop: asyncio.AbstractEventLoop) -> None:
        """ Serve CLI interface in a non-blocking way """

        readline.parse_and_bind("tab: complete")
        while True:
            cmd = await loop.run_in_executor(None, input, '>')
            await self.run_cmd(cmd)
            await asyncio.sleep(0)

    async def run_cmd(self, cmd: str) -> None:
        """ Execute the command from CLI """
        self.display(f'>{cmd}')
        try:
            sth = self.runner(cmd)
            if asyncio.iscoroutine(sth):
                self.display(await sth)
            else:
                self.display(sth)
        except Exception as e:
            self.display(e)

    @staticmethod
    def display(obj: Any) -> None:
        """ Print the string without messing the CLI input buffer """

        # Have to do this encoding/decoding bullshit because python fails to encode some symbols by default
        log_lines = f'{obj}'.encode(sys.stdout.encoding, 'ignore').decode(sys.stdout.encoding)

        # Save the user input line
        line_buffer = readline.get_line_buffer()
        # save cursor position, erase line, write log lines, write user input, restore cursor position,
        sys.stdout.write("\033[s\r\n\033[F\033[K" + log_lines + '\r\n>' + line_buffer + "\033[u")

    def format(self, record):
        return datetime.now().strftime("%d.%m %H:%M:%S") + ' ' + super().format(record)

    def emit(self, record) -> None:
        if record.levelno in [logging.ERROR, logging.CRITICAL]:
            self.display(u'\u001b[31m' + self.format(record) + u'\u001b[0m')
        elif record.levelno == logging.WARNING:
            self.display(u'\u001b[33m' + self.format(record) + u'\u001b[0m')
        else:
            self.display(self.format(record))
