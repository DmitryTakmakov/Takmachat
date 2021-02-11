"""
GUI for adding a new client.
"""
from logging import getLogger

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QComboBox

LOGGER = getLogger('client')


class AddContactDialog(QDialog):
    """
    Main GUI class.
    """

    def __init__(self, socket, db):
        """
        Initialization of GUI.

        :param socket: client's socket
        :param db: client's database
        """
        super().__init__()
        self.socket = socket
        self.db = db

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для добавления.')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.cntct_selector_label = QLabel(
            'Выберите контакт для добавления: ',
            self
        )
        self.cntct_selector_label.setFixedSize(250, 20)
        self.cntct_selector_label.move(10, 0)

        self.cntct_selector = QComboBox(self)
        self.cntct_selector.setFixedSize(200, 20)
        self.cntct_selector.move(10, 30)

        self.refresh_btn = QPushButton('Обновить', self)
        self.refresh_btn.setFixedSize(100, 30)
        self.refresh_btn.move(60, 60)

        self.ok_btn = QPushButton('Добавить', self)
        self.ok_btn.setFixedSize(100, 30)
        self.ok_btn.move(230, 20)

        self.cncl_btn = QPushButton('Отмена', self)
        self.cncl_btn.setFixedSize(100, 30)
        self.cncl_btn.move(230, 60)
        self.cncl_btn.clicked.connect(self.close)

        self.show_available_contacts()
        self.refresh_btn.clicked.connect(
            self.update_available_contacts
        )

    def show_available_contacts(self):
        """
        Show the list of available contacts in GUI.
        """
        self.cntct_selector.clear()
        contacts = set(self.db.get_contacts())
        users = set(self.db.get_existing_users())
        users.remove(self.socket.client_nickname)
        self.cntct_selector.addItems(users - contacts)

    def update_available_contacts(self):
        """
        Update the list of available contacts from the database.
        """
        try:
            self.socket.request_user_list()
        except OSError:
            pass
        else:
            LOGGER.debug(
                'Запрос списка пользователей выполнен успешно.'
            )
            self.show_available_contacts()
