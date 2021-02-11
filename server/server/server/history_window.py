"""
Modal GUI window with users' action history.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QPushButton, QTableView


class UserHistoryWindow(QDialog):
    """
    The main class of GUI.
    """

    def __init__(self, db):
        """
        Initialization of GUI.
        Creates all the necessary elements and the model with info to be displayed.

        :param db: server database
        """
        super().__init__()

        self.database = db

        self.setWindowTitle('История клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.user_history_table = QTableView(self)
        self.user_history_table.move(10, 10)
        self.user_history_table.setFixedSize(580, 620)

        self.create_message_history_model()

    def create_message_history_model(self):
        """
        Creates the model with users' history info.
        Queries the DB and adds entries to the model.
        """
        messages = self.database.get_message_history()
        history_list = QStandardItemModel()
        history_list.setHorizontalHeaderLabels(
            ['Логин пользователя',
             'Последняя активность',
             'Отправлено',
             'Получено'])
        for message in messages:
            login, active, sent, received = message
            login = QStandardItem(login)
            login.setEditable(False)
            active = QStandardItem(
                str(active.replace(microsecond=0)))
            active.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            received = QStandardItem(str(received))
            received.setEditable(False)
            history_list.appendRow([login, active, sent, received])
        self.user_history_table.setModel(history_list)
        self.user_history_table.resizeRowsToContents()
        self.user_history_table.resizeColumnsToContents()
