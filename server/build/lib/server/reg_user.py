"""
Modal GUI window for client registration.
"""
from binascii import hexlify
from hashlib import pbkdf2_hmac

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, \
    QPushButton, QMessageBox


class RegisterUser(QDialog):
    """
    Main class of GUI.
    """

    def __init__(self,
                 db,
                 server_thread):
        """
        Initialization of GUI.
        Sets up al the necessary elements, connects the
        "save" button to its handler.

        :param db: server database
        :param server_thread: server thread
        """
        super().__init__()

        self.db = db
        self.server = server_thread

        self.setWindowTitle('Регистрация пользователя')
        self.setFixedSize(265, 183)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.nickname_label = QLabel(
            'Введите имя пользователя:',
            self)
        self.nickname_label.move(10, 10)
        self.nickname_label.setFixedSize(200, 15)

        self.nickname_input = QLineEdit(self)
        self.nickname_input.move(10, 30)
        self.nickname_input.setFixedSize(245, 20)

        self.pwd_label = QLabel('Введите пароль:', self)
        self.pwd_label.move(10, 55)
        self.pwd_label.setFixedSize(200, 15)

        self.pwd_input = QLineEdit(self)
        self.pwd_input.move(10, 75)
        self.pwd_input.setFixedSize(245, 20)
        self.pwd_input.setEchoMode(QLineEdit.Password)

        self.pwd_conf_label = QLabel('Подтверждение пароля:', self)
        self.pwd_conf_label.move(10, 100)
        self.pwd_conf_label.setFixedSize(200, 15)

        self.pwd_conf_input = QLineEdit(self)
        self.pwd_conf_input.move(10, 120)
        self.pwd_conf_input.setFixedSize(245, 20)
        self.pwd_conf_input.setEchoMode(QLineEdit.Password)

        self.ok_btn = QPushButton('Сохранить', self)
        self.ok_btn.move(35, 150)
        self.ok_btn.clicked.connect(self.save_user)

        self.no_btn = QPushButton('Сбросить', self)
        self.no_btn.move(150, 150)
        self.no_btn.clicked.connect(self.close)

        self.messages = QMessageBox()

    def save_user(self):
        """
        Validates the entered values and triggers relevant
        messages if the data is not correct. Otherwise, generates
        the hashed password, registers the user in the DB and prompts
        the server to update the active users' list.
        """
        if not self.nickname_input.text():
            self.messages.critical(
                self,
                'Ошибка!',
                'Не указано имя пользователя!',
            )
            return
        elif self.pwd_input.text() != self.pwd_conf_input.text():
            self.messages.critical(
                self,
                'Ошибка!',
                'Пароли не совпадают!'
            )
            return
        elif self.db.check_existing_user(self.nickname_input.text()):
            self.messages.critical(
                self,
                'Ошибка!',
                'Пользователь с таким именем уже существует!'
            )
            return
        else:
            pwd_bytes = self.pwd_input.text().encode('utf-8')
            salt = self.nickname_input.text().lower().encode('utf-8')
            pwd_hash = pbkdf2_hmac('sha512', pwd_bytes, salt, 10000)
            self.db.register_user(self.nickname_input.text(),
                                  hexlify(pwd_hash))
            self.messages.information(
                self,
                'Успех!',
                'Пользователь успешно зарегистрирован!'
            )
            self.server.update_list()
            self.close()
