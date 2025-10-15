import random
import re
from typing import Iterable, Callable
from prettytable import PrettyTable


class Colors:
    MAUVE = 0xca9ee6
    RED = 0xe78284
    PEACH = 0xef9f76
    YELLOW = 0xe5c890
    GREEN = 0xa6d189
    BLUE = 0x8caaee
    BRIGHT = 0xa5adce
    DARK = 0x51576d
    DISCORD = 0x5865F2


def yield_parts(lines: list[str], limit: int = 2000, prefix: str = '', suffix: str = ''):
    """
    Yields pieces of text with limited length and prefix and suffix attached.
    Useful for splitting large messages into parts.
    """
    _limit = limit - len(prefix + suffix) - len('\n')
    _string = ''

    for line in lines:
        if len(_string) + len(line) > _limit:
            yield prefix + _string + suffix
            _string = line
            continue
        _string += '\n' + line

    if len(_string):
        yield prefix + _string + suffix


def random_string(length):
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(letters) for _ in range(length))


def find(f: Callable, it: Iterable):
    """
    Return first matching object or None from an iterable.
    Example usage: find(lambda i: i == 'a', it)
    """
    for item in it:
        if f(item):
            return item


def parse_user_mention(mention: str) -> str:
    """ discord user mention string to user_id """
    if (match := re.match(r"<@!?(\d+)>", mention)) is not None:
        try:
            return match.group(1)
        except KeyError:
            raise ValueError(f'Invalid mention {mention}.')


class AsciiTable:

    def __init__(self, title: str = None, columns: list[str] = None):
        self.table = PrettyTable(title=self.bold(title) if title else None, header=False, border=False)
        if columns:
            self.table.add_row([self.gray(s) for s in columns])

    def add_row(self, row: list[str]):
        self.table.add_row(row)

    def get_string(self) -> str:
        return '```ansi\n' + self.table.get_string() + '```'

    @staticmethod
    def bold(s: str) -> str:
        return f"\u001b[1m{s}\u001b[0m"

    @staticmethod
    def gray(s: str) -> str:
        return f"\u001b[0;30m{s}\u001b[0;0m"

    @staticmethod
    def red(s: str) -> str:
        return f"\u001b[0;31m{s}\u001b[0;0m"

    @staticmethod
    def green(s: str) -> str:
        return f"\u001b[0;32m{s}\u001b[0;0m"

    @staticmethod
    def yellow(s: str) -> str:
        return f"\u001b[0;33m{s}\u001b[0;0m"

    @staticmethod
    def blue(s: str) -> str:
        return f"\u001b[0;34m{s}\u001b[0;0m"

    @staticmethod
    def pink(s: str) -> str:
        return f"\u001b[0;35m{s}\u001b[0;0m"

    @staticmethod
    def cyan(s: str) -> str:
        return f"\u001b[0;36m{s}\u001b[0;0m"

    @staticmethod
    def white(s: str) -> str:
        return f"\u001b[0;37m{s}\u001b[0;0m"


def escape_markdown(text: str, *, as_needed: bool = False, ignore_links: bool = True) -> str:
    r"""A helper function that escapes Discord's markdown.

    Parameters
    ----------
    text: :class:`str`
        The text to escape markdown from.
    as_needed: :class:`bool`
        Whether to escape the markdown characters as needed. This
        means that it does not escape extraneous characters if it's
        not necessary, e.g. ``**hello**`` is escaped into ``\*\*hello**``
        instead of ``\*\*hello\*\*``. Note however that this can open
        you up to some clever syntax abuse. Defaults to ``False``.
    ignore_links: :class:`bool`
        Whether to leave links alone when escaping markdown. For example,
        if a URL in the text contains characters such as ``_`` then it will
        be left alone. This option is not supported with ``as_needed``.
        Defaults to ``True``.

    Returns
    -------
    :class:`str`
        The text with the markdown special characters escaped with a slash.
    """

    _MARKDOWN_ESCAPE_SUBREGEX = "|".join(
        r"\{0}(?=([\s\S]*((?<!\{0})\{0})))".format(c) for c in ("*", "`", "_", "~", "|")
    )
    _MARKDOWN_ESCAPE_COMMON = r"^>(?:>>)?\s|\[.+\]\(.+\)"
    _MARKDOWN_ESCAPE_REGEX = re.compile(
        rf"(?P<markdown>{_MARKDOWN_ESCAPE_SUBREGEX}|{_MARKDOWN_ESCAPE_COMMON})",
        re.MULTILINE,
    )
    _URL_REGEX = r"(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])"
    _MARKDOWN_STOCK_REGEX = rf"(?P<markdown>[_\\~|\*`]|{_MARKDOWN_ESCAPE_COMMON})"

    if not as_needed:

        def replacement(match: re.Match[str]):
            groupdict = match.groupdict()
            is_url = groupdict.get("url")
            if is_url:
                return is_url
            return "\\" + groupdict["markdown"]

        regex = _MARKDOWN_STOCK_REGEX
        if ignore_links:
            regex = f"(?:{_URL_REGEX}|{regex})"
        return re.sub(regex, replacement, text, count=0, flags=re.MULTILINE)

    text = re.sub(r"\\", r"\\\\", text)
    return _MARKDOWN_ESCAPE_REGEX.sub(r"\\\1", text)


def parse_duration(string):
    """ Parse a duration string (/slash command argument or such) """
    if string == 'inf':
        return 0

    duration = float(string[:-1])
    if string[-1] == 's':
        duration = duration
    elif string[-1] == 'm':
        duration = duration * 60
    elif string[-1] == 'h':
        duration = duration * 60 * 60
    elif string[-1] == 'd':
        duration = duration * 60 * 60 * 24
    elif string[-1] == 'W':
        duration = duration * 60 * 60 * 24 * 7
    elif string[-1] == 'M':
        duration = duration * 60 * 60 * 24 * 30
    elif string[-1] == 'Y':
        duration = duration * 60 * 60 * 24 * 30
    else:
        raise ValueError()
    return int(duration)
