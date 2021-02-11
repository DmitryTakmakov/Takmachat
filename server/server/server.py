"""
The main module of the server application, includes parsers for
command line arguments, configuration file and the main loop.
The main server loop works the following way:
first it acquires the launch and configuration parameters, then
launches the server thread and initializes the GUI.
"""
import os
from argparse import ArgumentParser
from configparser import ConfigParser
from logging import getLogger
from sys import argv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from server.core import MessagingServer
from server.gui import MainWindow
from server.database import ServerDatabase
from utils.constants import DEFAULT_CONNECTION_PORT
from utils.decorators import function_log

SERVER_LOGGER = getLogger('server')


@function_log
def get_launch_params(def_address: str, def_port: str) -> tuple:
    """
    Acquires the launching parameters for the server.

    :param def_address: default IP address (localhost)
    :param def_port: default port (7777)
    """
    SERVER_LOGGER.debug(
        'Инициализация парсера аргументов командной строки: %s' %
        argv)
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        '-a',
        '--addr',
        default=def_address,
        nargs='?',
        help='ip-адрес сервера, по умолчанию localhost.'
    )
    arg_parser.add_argument(
        '-p',
        '--port',
        default=def_port,
        type=int,
        nargs='?',
        help='порт, который прослушивается сервером.'
    )
    arg_parser.add_argument(
        '-n',
        '--no_gui',
        action='store_true'
    )
    namespace = arg_parser.parse_args(argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    gui_flag = namespace.no_gui
    SERVER_LOGGER.info('Аргументы загружены')
    return server_address, server_port, gui_flag


@function_log
def get_config_params() -> ConfigParser:
    """
    Acquires the configuration parameters for the server.
    """
    config = ConfigParser()
    cwd = os.getcwd()
    config.read(f"{cwd}/server_config.ini")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'db_path', '')
        config.set('SETTINGS', 'db_file', 'serverdb.sqlite3')
        config.set(
            'SETTINGS', 'default_port', str(DEFAULT_CONNECTION_PORT))
        config.set('SETTINGS', 'listen_address', '')
        return config


@function_log
def main_cycle():
    """
    The main server loop.
    Acquires the launch and configuration parameters,
    launches the server thread and initializes the GUI.
    """
    server_config = get_config_params()
    directory = os.getcwd()
    server_config.read(f"{directory}/{'server_config.ini'}")

    address, port, no_gui = get_launch_params(
        server_config['SETTINGS']['listen_address'],
        server_config['SETTINGS']['default_port']
    )
    database = ServerDatabase(
        os.path.join(
            server_config['SETTINGS']['db_path'],
            server_config['SETTINGS']['db_file']
        )
    )

    server = MessagingServer(address, port, database)
    server.setDaemon(True)
    server.start()

    if no_gui:
        while True:
            prompt = input('Для выхода введите exit: ')
            if prompt == 'exit':
                server.working = False
                server.join()
                break
    else:
        server_app = QApplication(argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(server, database, server_config)

        server_app.exec_()

        server.working = False


if __name__ == '__main__':
    main_cycle()
