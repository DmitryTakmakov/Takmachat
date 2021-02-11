"""
Settings for the client's logger.
"""

import os
import sys
from logging import Formatter, StreamHandler, ERROR, FileHandler, \
    getLogger

from utils.constants import CURRENT_LOGGING_LEVEL

sys.path.append('../')

CLIENT_LOG_FORMATTER = Formatter(
    '%(asctime)-10s %(levelname)-10s %(filename)-10s %(message)s'
)

filepath = os.getcwd()
filepath = os.path.join(filepath, 'logs/client.log')

stderr_logger = StreamHandler(sys.stderr)
stderr_logger.setFormatter(CLIENT_LOG_FORMATTER)
stderr_logger.setLevel(ERROR)
file_logger = FileHandler(filepath, encoding='utf-8')
file_logger.setFormatter(CLIENT_LOG_FORMATTER)

# создаем и настраиваем логгер
client_logger = getLogger('client')
client_logger.addHandler(stderr_logger)
client_logger.addHandler(file_logger)
client_logger.setLevel(CURRENT_LOGGING_LEVEL)
