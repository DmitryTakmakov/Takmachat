"""
The main module for client's application. Includes parser for command line
arguments and the main loop. The main loop works the following way:
Launches the app. If there's no nickname provided, prompts the login dialog.
Otherwise generates the public key (in case it's the first launch), opens a client's
socket and starts the GUI.
"""
import os
from argparse import ArgumentParser
from logging import getLogger

from sys import argv, exit as sys_exit

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

from client.database import ClientDatabase
from client.main_window import MainWindowClient
from client.core import ClientSocket
from client.start_window import ClientLoginDialog
from utils.errors import ServerError
from utils.constants import DEFAULT_IP_ADDR, DEFAULT_CONNECTION_PORT

CLIENT_LOGGER = getLogger('client')


def get_launch_params() -> tuple:
    """
    Acquires the launching parameters for the client's app.
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        '-a',
        '--address',
        default=DEFAULT_IP_ADDR,
        nargs='?',
        help='ip-адрес для подключения клиента'
    )
    arg_parser.add_argument(
        '-p',
        '--port',
        default=DEFAULT_CONNECTION_PORT,
        type=int,
        nargs='?',
        help='порт для подключения клиента'
    )
    arg_parser.add_argument(
        '-n',
        '--nickname',
        type=str,
        nargs='?',
        help='никнейм клиента'
    )
    arg_parser.add_argument(
        '-pw',
        '--password',
        default='',
        nargs='?',
        help='пароль клиента'
    )
    namespace = arg_parser.parse_args(argv[1:])
    addr = namespace.address
    prt = namespace.port
    ncknme = namespace.nickname
    pwd = namespace.password
    if not 1023 < prt < 65536:
        CLIENT_LOGGER.critical(
            'Попытка запустить приложение-клиент с недопустимым '
            'портом: %s. Порт должен быть в пределах от 1024 до '
            '65535. Приложение завершено.' % prt
        )
        sys_exit(1)
    return addr, prt, ncknme, pwd


def main_cycle():
    """
    The main loop of the client.
    Launches the app. If there's no nickname provided, prompts the login dialog.
    Otherwise generates the public key (in case it's the first launch),
    opens a client's socket and starts the GUI.
    """
    address, port, nickname, password = get_launch_params()
    client_socket = None
    client_app = QApplication(argv)
    welcome_dialog = ClientLoginDialog()
    if not nickname or not password:
        client_app.exec_()
        if welcome_dialog.ok_flag:
            nickname = welcome_dialog.nickname.text()
            password = welcome_dialog.password.text()
        else:
            sys_exit(0)

    CLIENT_LOGGER.info(
        'Запущено приложение-клиент с параметрами: '
        'адрес сервера - %s, серверный порт - '
        '%s, никнейм клиента - %s.' %
        (address, port, nickname)
    )

    cur_dir = os.getcwd()
    key_file = os.path.join(cur_dir, f'{nickname}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            pub_keys = RSA.import_key(key.read())

    client_db = ClientDatabase(nickname)
    try:
        client_socket = ClientSocket(
            address,
            port,
            nickname,
            client_db,
            password,
            pub_keys
        )
    except ServerError as e:
        msg = QMessageBox()
        msg.critical(
            welcome_dialog,
            'Ошибка сервера!',
            e.error_message
        )
        CLIENT_LOGGER.error(
            'При подключении сервер вернул ошибку: %s' %
            e.error_message)
        sys_exit(1)
    else:
        client_socket.setDaemon(True)
        client_socket.start()

    del welcome_dialog

    client_main_window = MainWindowClient(
        client_db, client_socket, pub_keys)
    client_main_window.establish_connection(client_socket)
    client_main_window.setWindowTitle(
        "Takmachat pre-alpha - %s" % nickname)
    client_app.exec_()

    client_socket.shutdown_socket()
    client_socket.join()


if __name__ == '__main__':
    main_cycle()
