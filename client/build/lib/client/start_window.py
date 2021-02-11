"""
GUI window to log into client's account.
"""
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, \
    QPushButton, qApp


class ClientLoginDialog(QDialog):
    """
    The main class of the GUI.
    """

    def __init__(self):
        """
        Initialization of GUI.
        Creates all the components of the window, connects
        the click event on the OK button to the handler.
        """
        super().__init__()

        self.ok_flag = False

        self.setWindowTitle("Вход / регистрация")
        self.setFixedSize(225, 160)

        self.nickname_label = QLabel(
            'Введите имя пользователя:',
            self
        )
        self.nickname_label.setFixedSize(200, 15)
        self.nickname_label.move(10, 10)

        self.nickname = QLineEdit(self)
        self.nickname.setFixedSize(200, 20)
        self.nickname.move(10, 35)

        self.password_label = QLabel(
            'Введите пароль:',
            self
        )
        self.password_label.setFixedSize(200, 15)
        self.password_label.move(10, 65)

        self.password = QLineEdit(self)
        self.password.setFixedSize(200, 20)
        self.password.move(10, 90)
        self.password.setEchoMode(QLineEdit.Password)

        self.ok_btn = QPushButton('Вход', self)
        self.ok_btn.move(10, 120)
        self.ok_btn.clicked.connect(self.btn_click)

        self.cancel_btn = QPushButton('Выход', self)
        self.cancel_btn.move(130, 120)
        self.cancel_btn.clicked.connect(qApp.exit)

        self.show()

    def btn_click(self):
        """
        Handles the click on the OK button, changes the flag to True.
        """
        if self.nickname.text():
            self.ok_flag = True
            qApp.exit()
