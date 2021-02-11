"""
GUI of the main window of server app.
"""
from configparser import ConfigParser

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, \
    QTableView

from server.config_window import ConfigWindow
from server.history_window import UserHistoryWindow
from server.reg_user import RegisterUser
from server.rem_user import RemoveUser


class MainWindow(QMainWindow):
    """
    Main class of GUI.
    """

    def __init__(self,
                 server,
                 db,
                 config: ConfigParser):
        """
        GUI initialization.
        Creates all the elements, creates the status bar and connects
        all the buttons to their respective handlers.

        :param server: server thread
        :param db: server database
        :param config: server configuration file
        """
        super().__init__()
        self.server_thread = server
        self.database = db
        self.config = config

        self.exit_button = QAction('Выход', self)
        self.exit_button.setShortcut('Ctrl+Q')
        self.exit_button.triggered.connect(qApp.quit)

        self.refresh_users_list_button = QAction(
            'Обновить список клиентов', self)
        self.server_config_button = QAction(
            'Настройка сервера', self)
        self.user_history_button = QAction(
            'История пользователей', self)
        self.register_user_button = QAction(
            'Регистрация пользователя', self)
        self.delete_user_button = QAction(
            'Удаление пользователя', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.refresh_users_list_button)
        self.toolbar.addAction(self.user_history_button)
        self.toolbar.addAction(self.server_config_button)
        self.toolbar.addAction(self.register_user_button)
        self.toolbar.addAction(self.delete_user_button)
        self.toolbar.addAction(self.exit_button)

        self.setFixedSize(1025, 600)
        self.setWindowTitle('Messaging app server')

        self.label = QLabel('Список подключенных клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 32)

        self.active_users_table = QTableView(self)
        self.active_users_table.move(10, 50)
        self.active_users_table.setFixedSize(1005, 400)

        self.timer = QTimer()
        self.timer.timeout.connect(self.create_active_users_model)
        self.timer.start(1000)

        self.refresh_users_list_button.triggered.connect(
            self.create_active_users_model)
        self.server_config_button.triggered.connect(
            self.configure_server)
        self.user_history_button.triggered.connect(
            self.show_users_stats)
        self.register_user_button.triggered.connect(
            self.register_user)
        self.delete_user_button.triggered.connect(
            self.delete_user)

        self.show()

    def create_active_users_model(self):
        """
        Creates the model of all currently active users to show in the main
        window of the app. Queries the DB and adds entries to the model.
        """
        active_users = self.database.all_active_users_list()
        users_list = QStandardItemModel()
        users_list.setHorizontalHeaderLabels(
            ['Логин пользователя',
             'IP-адрес',
             'Порт',
             'Время подключения'])
        for user in active_users:
            login, ip, port, active = user
            login = QStandardItem(login)
            login.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            active = QStandardItem(
                str(active.replace(microsecond=0)))
            active.setEditable(False)
            users_list.appendRow([login, ip, port, active])
        self.active_users_table.setModel(users_list)
        self.active_users_table.resizeColumnsToContents()
        self.active_users_table.resizeRowsToContents()

    def show_users_stats(self):
        """
        Modal window with users' action history.
        """
        global stats_window
        stats_window = UserHistoryWindow(self.database)
        stats_window.show()

    def configure_server(self):
        """
        Modal window with server configuration.
        """
        global config_window
        config_window = ConfigWindow(self.config)
        config_window.show()

    def register_user(self):
        """
        Modal window with client registration.
        That is the only way someone can be registered in the chat.
        """
        global registration_window
        registration_window = RegisterUser(
            self.database, self.server_thread)
        registration_window.show()

    def delete_user(self):
        """
        Modal window with client deletion.
        """
        global remove_window
        remove_window = RemoveUser(
            self.database, self.server_thread)
        remove_window.show()
