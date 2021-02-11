"""
Logging decorators used in the project.
"""
from inspect import stack
from logging import getLogger
from sys import argv, path

import logs.client_log_config
import logs.server_log_config

if argv[0].find('client') == -1:
    LOGGER = getLogger('server')
else:
    LOGGER = getLogger('client')


def function_log(func):
    """
    The decorator function
    """

    def wrapper(*args, **kwargs):
        """
        Main function that does all the logging.
        """
        LOGGER.debug(
            'Функция %s была вызвана в модуле %s с '
            'параметрами (%s, %s). Вызов произошел из функции %s.' %
            (
                func.__name__,
                func.__module__,
                args,
                kwargs,
                stack()[1][3]
            ),
        )
        result = func(*args, **kwargs)
        return result

    return wrapper
