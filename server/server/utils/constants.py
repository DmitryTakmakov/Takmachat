"""
Constants used throughout the project.
"""

import logging

# порт для подключения по умолчанию
DEFAULT_CONNECTION_PORT = 7777
# айпи по умолчанию
DEFAULT_IP_ADDR = 'localhost'
# максимальное число соединений
MAX_NUMBER_OF_CONNECTIONS = 100
# максимальный размер пакета (сообщения)
MAX_PACK_LENGTH = 1024
# кодировка по умолчанию
DEFAULT_ENCODING = 'utf8'
# текущий уровень логирования
CURRENT_LOGGING_LEVEL = logging.DEBUG

# основные ключи для JIM-протокола
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# прочие ключи
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USER_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'
