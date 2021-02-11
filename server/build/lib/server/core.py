"""
All the main functions for the server app
"""
from binascii import hexlify, a2b_base64
from hmac import new, compare_digest
from json import JSONDecodeError
from logging import getLogger
from os import urandom
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from utils.constants import MAX_NUMBER_OF_CONNECTIONS, ACTION, \
    PRESENCE, TIME, USER, MESSAGE, SENDER, DESTINATION, \
    MESSAGE_TEXT, RESPONSE, ERROR, EXIT, ACCOUNT_NAME, GET_CONTACTS, \
    LIST_INFO, ADD_CONTACT, REMOVE_CONTACT, USER_REQUEST, \
    PUBLIC_KEY_REQUEST, DATA, PUBLIC_KEY
from utils.descriptors import Port
from utils.utils import receive_message, send_message

SERVER_LOGGER = getLogger('server')


class MessagingServer(Thread):
    """
    The main class of the server.
    """
    port = Port()

    def __init__(self,
                 listening_address: str,
                 listening_port: int,
                 db):
        """
        Server initialization.
        Creates the attributes needed for the server to work,
        sets the working flag as True.

        :param listening_address: server's IP address
        :param listening_port: server's port
        :param db: server's database
        """
        self.listening_address = listening_address
        self.listening_port = listening_port
        self.server_db = db
        self.server_socket = None
        self.clients_list = []
        self.sockets_list = None
        self.exceptions_list = None
        self.messages_queue = list()
        self.nicknames = dict()
        self.working = True
        super().__init__()

    def run(self):
        """
        The main loop of the server.
        Creates a listening socket, and then accepts connections while the working flag is True.
        If there are clients with messages, sends them.
        """
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(
            (self.listening_address, self.listening_port)
        )
        self.server_socket.settimeout(0.5)
        self.server_socket.listen(MAX_NUMBER_OF_CONNECTIONS)

        try:
            while self.working:
                try:
                    client_socket, client = self.server_socket.accept()
                    addr, port = client
                except OSError:
                    pass
                else:
                    SERVER_LOGGER.info(
                        'Установлено соединение с пользователем: '
                        'адрес: %s, порт: %s.' % (addr, port,)
                    )
                    client_socket.settimeout(5)
                    self.clients_list.append(client_socket)
                ready_to_receive = []
                ready_to_send = []
                exceptions_list = []
                try:
                    if self.clients_list:
                        ready_to_send, self.sockets_list, self.exceptions_list = select(
                            self.clients_list,
                            self.clients_list,
                            [],
                            0
                        )
                except OSError as err:
                    SERVER_LOGGER.error(
                        'Ошибка работы с сокетами: %s.' % err
                    )
                if ready_to_send:
                    for client in ready_to_send:
                        try:
                            self.process_client_message(
                                receive_message(client),
                                client
                            )
                        except (OSError,
                                JSONDecodeError,
                                TypeError) as e:
                            SERVER_LOGGER.error(
                                'Ошибка при запросе '
                                'информации от клиента.',
                                exc_info=e
                            )
                            self.delete_client(client)
        except KeyboardInterrupt:
            SERVER_LOGGER.info('Серер остановлен пользователем.')
            self.server_socket.close()

    def process_client_message(self, message: dict, client: socket):
        """
        Handles the messages from clients according to their service codes.
        This method handles authorization, client's exit, contact list, existing users'
        and public key requests, requests to add or delete a contact and messages from
        client to client (this method also records these messages to server DB). This method
        triggers a relevant handler if needed, or tries to send a response with a relevant
        service code (200, 202, 511 or 400 in case of bad request). If sending a message
        was not possible, this method deletes the user from the list of active users.

        :param message: dictionary with a message
        :param client: client's socket
        """
        SERVER_LOGGER.debug(
            'Обработка входящего сообщения: %s.' % message
        )
        # авторизация клиента
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            self.authorize_client(message, client)
        # сообщение от клиента
        elif ACTION in message and message[ACTION] == MESSAGE and \
                SENDER in message and DESTINATION in message and \
                TIME in message and MESSAGE_TEXT in message \
                and self.nicknames[message[SENDER]] == client:
            if message[DESTINATION] in self.nicknames:
                self.messages_queue.append(message)
                self.server_db.record_message_to_history(
                    message[SENDER],
                    message[DESTINATION]
                )
                self.send_client_message(message)
                try:
                    send_message(client, {RESPONSE: 200})
                except OSError:
                    self.delete_client(client)
            else:
                response = {
                    RESPONSE: 400,
                    ERROR: 'Пользователь не зарегистрирован на сервере.'
                }
                try:
                    send_message(client, response)
                except OSError:
                    pass
            return
        # клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and \
                ACCOUNT_NAME in message:
            self.delete_client(client)
        # запрос списка контактов
        elif ACTION in message and message[ACTION] == GET_CONTACTS \
                and USER in message \
                and self.nicknames[message[USER]] == client:
            response = {
                RESPONSE: 202,
                LIST_INFO: self.server_db.get_user_contact_list(
                    message[USER])
            }
            try:
                send_message(client, response)
            except OSError:
                self.delete_client(client)
        # запрос на добавление контакта
        elif ACTION in message and message[ACTION] == ADD_CONTACT \
                and ACCOUNT_NAME in message and USER in message \
                and self.nicknames[message[USER]] == client:
            self.server_db.add_contact_to_list(
                message[USER],
                message[ACCOUNT_NAME]
            )
            try:
                send_message(client, {RESPONSE: 200})
            except OSError:
                self.delete_client(client)
        # запрос на удаление контакта
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT \
                and ACCOUNT_NAME in message and USER in message \
                and self.nicknames[message[USER]] == client:
            self.server_db.remove_contact_from_list(
                message[USER],
                message[ACCOUNT_NAME]
            )
            try:
                send_message(client, {RESPONSE: 200})
            except OSError:
                self.delete_client(client)
        # запрос списка пользователей
        elif ACTION in message and message[ACTION] == USER_REQUEST \
                and ACCOUNT_NAME in message \
                and self.nicknames[message[ACCOUNT_NAME]] == client:
            response = {
                RESPONSE: 202,
                LIST_INFO: [
                    user[0] for user in self.server_db.all_users_list()
                ]
            }
            try:
                send_message(client, response)
            except OSError:
                self.delete_client(client)
        # запрос публичного ключа клиента
        elif ACTION in message and message[ACTION] == \
                PUBLIC_KEY_REQUEST and ACCOUNT_NAME in message:
            response = {
                RESPONSE: 511,
                DATA: self.server_db.get_user_public_key(
                    message[ACCOUNT_NAME])
            }
            if response[DATA]:
                try:
                    send_message(client, response)
                except OSError:
                    self.delete_client(client)
            else:
                response = {
                    RESPONSE: 400,
                    ERROR: 'Отсутствует публичный ключ пользователя.'
                }
                try:
                    send_message(client, response)
                except OSError:
                    self.delete_client(client)
        else:
            response = {
                RESPONSE: 400,
                ERROR: 'bad request'
            }
            try:
                send_message(client, response)
            except OSError:
                self.delete_client(client)

    def authorize_client(self, message: dict, client: socket):
        """
        Handles the client's authorization. Checks if the username isn't already taken,
        then checks if the user is registered on the server. If those two checks pass,
        the method then initiates the exchange of encrypted passwords with the client.
        If the password is correct, the client is logged onto the server, otherwise the
        client is removed from the server and his socket gets closed.

        :param message: presence message
        :param client: client's socket
        """
        SERVER_LOGGER.debug(
            'Старт процесса авторизации пользователя %s' %
            message[USER]
        )
        if message[USER][ACCOUNT_NAME] in self.nicknames.keys():
            response = {
                RESPONSE: 400,
                ERROR: 'Имя пользователя уже занято'
            }
            try:
                send_message(client, response)
            except OSError as e:
                SERVER_LOGGER.debug('Произошла ошибка: %s' % e)
                pass
            self.clients_list.remove(client)
            client.close()
        elif not self.server_db.check_existing_user(
                message[USER][ACCOUNT_NAME]):
            response = {
                RESPONSE: 400,
                ERROR: 'Пользователь не зарегистрирован'
            }
            try:
                SERVER_LOGGER.debug(
                    'Пользователь %s не зарегистрирован' %
                    message[USER][ACCOUNT_NAME]
                )
                send_message(client, response)
            except OSError as e:
                SERVER_LOGGER.debug('Произошла ошибка: %s' % e)
                pass
        else:
            SERVER_LOGGER.debug('Начало проверки пароля')
            random_string = hexlify(urandom(64))
            auth_response = {
                RESPONSE: 511,
                DATA: random_string.decode('ascii')
            }
            pwd_hash = new(
                self.server_db.get_user_pwd_hash(
                    message[USER][ACCOUNT_NAME]),
                random_string,
                'MD5'
            )
            pwd_digest = pwd_hash.digest()
            SERVER_LOGGER.debug(
                'Подготовлено сообщение для авторизации: %s' %
                auth_response
            )
            try:
                send_message(client, auth_response)
                client_response = receive_message(client)
            except OSError as e:
                SERVER_LOGGER.debug(
                    'Ошибка при авторизации: ', exc_info=e
                )
                client.close()
                return
            client_digest = a2b_base64(client_response[DATA])
            if RESPONSE in client_response and \
                    client_response[RESPONSE] == 511 and \
                    compare_digest(pwd_digest, client_digest):
                self.nicknames[message[USER][ACCOUNT_NAME]] = client
                client_addr, client_port = client.getpeername()
                try:
                    send_message(client, {RESPONSE: 200})
                except OSError:
                    self.delete_client(client)
                self.server_db.login_user(
                    message[USER][ACCOUNT_NAME],
                    client_addr,
                    client_port,
                    message[USER][PUBLIC_KEY]
                )
            else:
                response = {
                    RESPONSE: 400,
                    ERROR: 'Неверный пароль'
                }
                try:
                    send_message(client, response)
                except OSError:
                    pass
                self.clients_list.remove(client)
                client.close()

    def send_client_message(self, message: dict):
        """
        Handles the exchange of messages between clients.
        Validates the message and sends it if correct

        :param message: dictionary with the message
        """
        if message[DESTINATION] in self.nicknames and \
                self.nicknames[message[DESTINATION]] in \
                self.sockets_list:
            send_message(self.nicknames[message[DESTINATION]],
                         message)
            SERVER_LOGGER.info(
                'Было отправлено сообщение пользователю '
                '%s от пользователя %s.' %
                (message[DESTINATION], message[SENDER])
            )
        elif message[DESTINATION] in self.nicknames and \
                self.nicknames[message[DESTINATION]] \
                not in self.sockets_list:
            SERVER_LOGGER.error(
                'Потеряна связь с клиентом %s, '
                'отправка сообщения не возможна.' %
                self.nicknames[message[DESTINATION]]
            )
            self.delete_client(self.nicknames[message[DESTINATION]])
        else:
            SERVER_LOGGER.error(
                'Пользователь %s не зарегистрирован на сервере, '
                'отправка сообщения не возможна.' %
                message[DESTINATION]
            )

    def delete_client(self, client: socket):
        """
        Closes the connection with the client who decided to leave the server.
        Logs him out in the DB, deletes from the list of active users and closes the socket.

        :param client: client's socket
        """
        SERVER_LOGGER.info(
            'Клиент %s отключился от сервера' % client)
        for name in self.nicknames:
            if self.nicknames[name] == client:
                self.server_db.logout_user(name)
                del self.nicknames[name]
                break
        self.clients_list.remove(client)
        client.close()

    def update_list(self):
        """
        Generates the message with 205 code that triggers the update of contact
        and active users' lists for all active clients.
        """
        for name in self.nicknames:
            try:
                send_message(self.nicknames[name], {RESPONSE: 205})
            except OSError:
                self.delete_client(self.nicknames[name])
