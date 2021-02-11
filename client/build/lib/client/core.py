"""
Client's socket module.
"""
from binascii import hexlify, b2a_base64
from hashlib import pbkdf2_hmac
from hmac import new
from json import JSONDecodeError
from logging import getLogger
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep, time

from Crypto.PublicKey.RSA import RsaKey
from PyQt5.QtCore import QObject, pyqtSignal

from utils.constants import ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, SENDER, DESTINATION, \
    MESSAGE_TEXT, GET_CONTACTS, LIST_INFO, USER_REQUEST, \
    ADD_CONTACT, REMOVE_CONTACT, EXIT, PUBLIC_KEY, DATA, \
    PUBLIC_KEY_REQUEST
from utils.decorators import function_log
from utils.errors import ServerError
from utils.utils import send_message, receive_message

SOCKET_LOGGER = getLogger('client')
socket_lock = Lock()


class ClientSocket(Thread, QObject):
    """
    Main class of client's socket.
    """
    new_msg_signal = pyqtSignal(dict)
    msg_205_signal = pyqtSignal()
    connection_lost = pyqtSignal()

    def __init__(self,
                 server_address: str,
                 server_port: int,
                 client_nickname: str,
                 database,
                 password: str,
                 keys: RsaKey):
        """
        Initialization of client's socket.
        Requests the contacts and existing users' lists,
        connects to the server and sets the running flag to True.

        :param server_address: server's IP address
        :param server_port: listening port on the server
        :param client_nickname: client's login
        :param database: client's DB
        :param password: client's password, duh
        :param keys: client's RSA key
        """
        Thread.__init__(self)
        QObject.__init__(self)
        self.client_nickname = client_nickname
        self.database = database
        self.client_socket = None
        self.password = password
        self.keys = keys
        self.establish_connection(server_address, server_port)
        self.pubkey = None
        try:
            self.request_contacts()
            self.request_user_list()
        except OSError as e:
            if e.errno:
                SOCKET_LOGGER.critical(
                    'Потеряно соединение с сервером.'
                )
                raise ServerError('Потеряно соединение с сервером.')
            SOCKET_LOGGER.error(
                'Таймаут соединения с сервером '
                'при запросе списков пользователей.')
        except JSONDecodeError:
            SOCKET_LOGGER.critical('Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером.')
        self.running = True

    def establish_connection(self, ip_address: str, port: int):
        """
        Establishes connection to the server.
        Makes 5 attempts to do so, if unsuccessful, ends the cycle.
        If successful, sends the presence message to the server,
        and then, sends the encrypted password to the server to
        compare to the one stored in the server's DB.

        :param ip_address: server's IP address
        :param port: server's listening port
        """
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.settimeout(5)
        connected = False

        for i in range(5):
            SOCKET_LOGGER.info('Попытка соединения №%d' % (i + 1,))
            try:
                self.client_socket.connect((ip_address, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            sleep(1)

        if not connected:
            SOCKET_LOGGER.critical(
                'Не удалось установить соединение с сервером.'
            )
            raise ServerError(
                'Не удалось установить соединение с сервером.'
            )

        SOCKET_LOGGER.debug(
            'Установлено соединение с сервером. '
            'Начинаю процесс авторизации.'
        )

        password_bytes = self.password.encode('utf-8')
        salt = self.client_nickname.lower().encode('utf-8')
        password_hash = pbkdf2_hmac(
            'sha512',
            password_bytes,
            salt,
            10000
        )
        password_hash_str = hexlify(password_hash)

        SOCKET_LOGGER.debug(
            'Подготовлен хэш пароля: %s' % password_hash_str
        )

        self.pubkey = self.keys.publickey().export_key().decode(
            'ascii')
        with socket_lock:
            msg = self.establish_presence()
            try:
                send_message(
                    self.client_socket,
                    msg
                )
                server_response = receive_message(self.client_socket)
                SOCKET_LOGGER.debug(
                    'Ответ сервера - %s' % server_response
                )
                if RESPONSE in server_response:
                    if server_response[RESPONSE] == 400:
                        raise ServerError(server_response[ERROR])
                    elif server_response[RESPONSE] == 511:
                        resp_data = server_response[DATA]
                        resp_hash = new(
                            password_hash_str,
                            resp_data.encode('utf-8'),
                            'MD5'
                        )
                        digest = resp_hash.digest()
                        client_response = {
                            RESPONSE: 511,
                            DATA: b2a_base64(digest).decode('ascii')
                        }
                        send_message(
                            self.client_socket,
                            client_response
                        )
                        self.process_answer(
                            receive_message(self.client_socket)
                        )
            except (OSError, JSONDecodeError):
                SOCKET_LOGGER.critical(
                    'В процессе авторизации потеряно '
                    'соединение с сервером'
                )
                raise ServerError(
                    'В процессе авторизации потеряно '
                    'соединение с сервером'
                )
            else:
                SOCKET_LOGGER.info('Соединение успешно установлено.')

    @function_log
    def establish_presence(self) -> dict:
        """
        Generates the presence message for the server.
        """
        message = {
            ACTION: PRESENCE,
            TIME: time(),
            USER: {
                ACCOUNT_NAME: self.client_nickname,
                PUBLIC_KEY: self.pubkey
            }
        }
        SOCKET_LOGGER.debug(
            "Сформировано %s сообщение для аккаунта %s."
            % (PRESENCE, self.client_nickname,)
        )
        return message

    @function_log
    def process_answer(self, message: dict):
        """
        Processes the server's response.
        Depending on the response code either: finishes working (200);
        raises ServerError (400); updates the lists and emits the relevant signal (205);
        or processes the message from another user, saves it to DB and emits the signal.

        :param message: message to process
        """
        SOCKET_LOGGER.debug(
            "Обработка сообщения от сервера: %s." % message
        )
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'400: {message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.request_user_list()
                self.request_contacts()
                self.msg_205_signal.emit()
            else:
                SOCKET_LOGGER.debug(
                    "Принят неизвестный ответ сервера: %s"
                    % message[RESPONSE]
                )
        elif ACTION in message and message[ACTION] == MESSAGE \
                and SENDER in message and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.client_nickname:
            SOCKET_LOGGER.info(
                'Получено сообщение от пользователя %s: %s'
                % (message[SENDER], message[MESSAGE_TEXT],)
            )
            self.database.save_message_to_history(
                message[SENDER],
                'in',
                message[MESSAGE_TEXT]
            )
            self.new_msg_signal.emit(message)

    def request_contacts(self):
        """
        Requests a contact list from the server.
        If the status code of the server's response is 202, updates
        the contact list in the client's DB.
        """
        SOCKET_LOGGER.debug(
            'Запрос списка контактов пользователя: %s'
            % self.client_nickname
        )
        self.database.cleat_contact_list()
        request = {
            ACTION: GET_CONTACTS,
            TIME: time(),
            USER: self.client_nickname
        }
        SOCKET_LOGGER.debug(
            'Сформирован запрос к серверу: %s' % request
        )
        with socket_lock:
            send_message(self.client_socket, request)
            response = receive_message(self.client_socket)
        SOCKET_LOGGER.debug(
            'Получен ответ от сервера: %s' % response
        )
        if RESPONSE in response and response[RESPONSE] == 202:
            for contact in response[LIST_INFO]:
                self.database.add_user_to_contacts(contact)
        else:
            SOCKET_LOGGER.error(
                'Не удалось обновить список контактов.'
            )

    def request_user_list(self):
        """
        Requests a list of existing users from the server.
        If the status code of the server's response is 202, updates
        the list in the client's DB.
        """
        SOCKET_LOGGER.info(
            'Пользователь %s запрашивает список всех пользователей.'
            % self.client_nickname
        )
        request = {
            ACTION: USER_REQUEST,
            TIME: time(),
            ACCOUNT_NAME: self.client_nickname
        }
        with socket_lock:
            send_message(self.client_socket, request)
            response = receive_message(self.client_socket)
        if RESPONSE in response and response[RESPONSE] == 202:
            self.database.add_existing_users(response[LIST_INFO])
        else:
            SOCKET_LOGGER.error(
                'Не удалось обновить список известных пользователей.'
            )

    def request_pub_key(self, user: str) -> str:
        """
        Requests a public RSA key for a client in user's contact list.
        If the status code in the server's response is 511, returns the key.

        :param user: contact
        """
        SOCKET_LOGGER.debug(
            'Запрос публичного ключа для пользователя %s' % user
        )
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            send_message(self.client_socket, request)
            response = receive_message(self.client_socket)
            if RESPONSE in response and response[RESPONSE] == 511:
                return response[DATA]
            else:
                SOCKET_LOGGER.error(
                    'Не удалось получить публичный ключ '
                    'пользователя %s' % user
                )

    def add_new_contact(self, contact: str):
        """
        Handles the adding of a new contact on the socket's side.
        Generates the relevant message and sends it to the server.

        :param contact: new contact
        """
        SOCKET_LOGGER.debug(
            'Создание нового контакта %s для пользователя %s' %
            (contact, self.client_nickname,)
        )
        request = {
            ACTION: ADD_CONTACT,
            TIME: time(),
            USER: self.client_nickname,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.client_socket, request)
            self.process_answer(receive_message(self.client_socket))

    def remove_contact(self, contact: str):
        """
        Handles the adding of a new contact on the socket's side.
        Generates the relevant message and sends it to the server.

        :param contact: contact to be deleted
        """
        SOCKET_LOGGER.debug(
            'Удаление контакта %s для пользователя %s' %
            (contact, self.client_nickname,)
        )
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time(),
            USER: self.client_nickname,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            send_message(self.client_socket, request)
            self.process_answer(
                receive_message(self.client_socket)
            )

    @function_log
    def shutdown_socket(self):
        """
        Handles the socket shutdown. Sets the running flag to False,
        generates the exit message to the server and sends it.
        """
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time(),
            ACCOUNT_NAME: self.client_nickname
        }
        with socket_lock:
            try:
                send_message(self.client_socket, message)
            except OSError:
                pass
        SOCKET_LOGGER.debug('Клиентский сокет завершает работу.')
        sleep(1)

    def create_message(self, recipient: str, message: str):
        """
        Creates and sends the dictionary with the message from one client to another.

        :param recipient: message's recipient
        :param message: message text
        """
        message_to_send_dict = {
            ACTION: MESSAGE,
            SENDER: self.client_nickname,
            DESTINATION: recipient,
            TIME: time(),
            MESSAGE_TEXT: message
        }
        SOCKET_LOGGER.debug(
            'Сформирован словарь сообщения: %s' %
            message_to_send_dict
        )
        with socket_lock:
            send_message(self.client_socket, message_to_send_dict)
            self.process_answer(receive_message(self.client_socket))
            SOCKET_LOGGER.info(
                'Отправлено сообщение пользователю %s' % recipient
            )

    def run(self):
        """
        The main loop of the client's app.
        While the running flag is True, it locks the socket and tries to receive
        messages from the server. Handles various exceptions and emits the
        lost connection signal.
        """
        SOCKET_LOGGER.debug(
            'Запущен процесс приема сообщений с сервера.'
        )
        while self.running:
            sleep(1)
            with socket_lock:
                try:
                    self.client_socket.settimeout(0.5)
                    server_response = receive_message(self.client_socket)
                except OSError as e:
                    if e.errno:
                        SOCKET_LOGGER.critical(
                            'Потеряно соединение с сервером.'
                        )
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError,
                        ConnectionAbortedError,
                        ConnectionRefusedError,
                        JSONDecodeError,
                        TypeError):
                    SOCKET_LOGGER.critical(
                        'Ошибка при соединении с сервером.'
                    )
                    self.running = False
                    self.connection_lost.emit()
                else:
                    SOCKET_LOGGER.debug(
                        'Принято сообщение с сервера: %s' %
                        server_response
                    )
                    self.process_answer(server_response)
                finally:
                    self.client_socket.settimeout(5)
