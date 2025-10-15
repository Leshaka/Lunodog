class BotException(BaseException):
    """ Base Bot exception class """
    pass


class BotPermissionError(BotException):
    """ Insufficient permissions to perform the bot operation """
    pass


class BotSyntaxError(BotException):
    """ Incorrect command arguments syntax """
    pass


class BotValueError(BotException):
    """ Improper value provided for a specific command argument """
    pass


class BotNotFoundError(BotException):
    """ Certain bot object is not found (queue, member, match, etc...) """
    pass


class MissingScope(BotException):
    """ Invoked command missing a proper scope (match thread, queue channel, etc...) """
    pass


class BotNotImplementedError(BotException):
    """ The command is not implemented inside this scope """
    pass
