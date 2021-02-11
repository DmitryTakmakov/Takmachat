"""
Modal GUI window for client removal.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton


class RemoveUser(QDialog):
    """
    Main class of GUI.
    """

    def __init__(self,
                 db,
                 server_thread):
        """
        Initialization of GUI.
        Sets up all the necessary elements, connects the button to their handlers
        and triggers the update of the list of existing users.

        :param db: server database
        :param server_thread: server thread
        """
        super().__init__()

        self.db = db
        self.server = server_thread

        self.setFixedSize(305, 100)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.user_select_label = QLabel(
            'Выберите пользователя для удаления:', self)
        self.user_select_label.move(10, 0)
        self.user_select_label.setFixedSize(280, 20)

        self.user_selector = QComboBox(self)
        self.user_selector.move(10, 30)
        self.user_selector.setFixedSize(280, 20)

        self.ok_btn = QPushButton('Удалить', self)
        self.ok_btn.setFixedSize(100, 30)
        self.ok_btn.move(10, 55)
        self.ok_btn.clicked.connect(self.remove_user)

        self.no_btn = QPushButton('Отмена', self)
        self.no_btn.setFixedSize(100, 30)
        self.no_btn.move(150, 55)
        self.no_btn.clicked.connect(self.close)

        self.update_selector()

    def remove_user(self):
        """
        Handles the deletion of the user. Checks if the user is registered
        on the server, deletes him and prompts the server to update the list of active users.
        """
        self.db.remove_user_from_db(self.user_selector.currentText())
        if self.user_selector.currentText() in self.server.nicknames:
            client = self.server.nicknames[
                self.user_selector.currentText()]
            del self.server.nicknames[
                self.user_selector.currentText()]
            self.server.delete_client(client)
        self.server.update_list()
        self.close()

    def update_selector(self):
        """
        Updates the list of active users in the selector.
        """
        self.user_selector.addItems(
            [item[0] for item in self.db.all_users_list()]
        )
