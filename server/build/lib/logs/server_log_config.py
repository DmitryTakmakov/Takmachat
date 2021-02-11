"""
Settings for the server's logger.
"""

import os
import sys
from logging import Formatter, StreamHandler, ERROR, getLogger
from logging.handlers import TimedRotatingFileHandler

from utils.constants import CURRENT_LOGGING_LEVEL

sys.path.append('../')

SERVER_LOG_FORMATTER = Formatter(
    '%(asctime)-10s %(levelname)-10s %(filename)-10s %(message)s'
)

filepath = os.getcwd()
filepath = os.path.join(filepath, 'logs/server.log')

stderr_logger = StreamHandler(sys.stderr)
stderr_logger.setFormatter(SERVER_LOG_FORMATTER)
stderr_logger.setLevel(ERROR)
file_logger = TimedRotatingFileHandler(
    filepath,
    encoding='utf-8',
    interval=1,
    when='D'
)
file_logger.setFormatter(SERVER_LOG_FORMATTER, )

server_logger = getLogger('server')
server_logger.addHandler(stderr_logger)
server_logger.addHandler(file_logger)
server_logger.setLevel(CURRENT_LOGGING_LEVEL)
