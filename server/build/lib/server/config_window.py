"""
GUI for server configuration window.
"""
import os
from configparser import ConfigParser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox


class ConfigWindow(QDialog):
    """
    Main GUI class
    """

    def __init__(self, config: ConfigParser):
        """
        Initialization of the GUI.
        Sets up all the elements and connects all the buttons
        to their respective handlers.

        :param config: configuration file
        """
        super().__init__()
        self.config = config

        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.path_to_db_label = QLabel('Путь к базе данных:', self)
        self.path_to_db_label.move(10, 10)
        self.path_to_db_label.setFixedSize(240, 15)

        self.path_to_db = QLineEdit(self)
        self.path_to_db.setFixedSize(250, 20)
        self.path_to_db.move(10, 30)
        self.path_to_db.setReadOnly(True)

        self.select_path_to_db_button = QPushButton('Обзор...', self)
        self.select_path_to_db_button.move(275, 28)

        self.database_file_name_label = QLabel(
            'Имя файла базы данных:', self)
        self.database_file_name_label.move(10, 68)
        self.database_file_name_label.setFixedSize(180, 15)

        self.database_file_name = QLineEdit(self)
        self.database_file_name.move(200, 66)
        self.database_file_name.setFixedSize(150, 20)

        self.port_label = QLabel('Номер порта сервера:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('Допустимые адреса:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(
            '*оставьте это поле пустым, чтобы принимать '
            '\nсоединения с любых адресов', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.select_path_to_db_button.clicked.connect(
            self.file_dialog_handler)
        self.save_button.clicked.connect(self.save_config_data)

        self.path_to_db.insert(self.config['SETTINGS']['db_path'])
        self.database_file_name.insert(
            self.config['SETTINGS']['db_file'])
        self.port.insert(self.config['SETTINGS']['default_port'])
        self.ip.insert(self.config['SETTINGS']['listen_address'])

    def file_dialog_handler(self):
        """
        Handles a modal window to choose the directory with the server DB.
        """
        global dialog_window
        dialog_window = QFileDialog(self)
        filepath = dialog_window.getExistingDirectory()
        filepath = filepath.replace('/', '\\')
        self.path_to_db.insert(filepath)

    def save_config_data(self):
        """
        Handles the modal window with server configuration data,
        checks the validity of the entered values and if they aren't
        valid triggers a relevant message. On success triggers a message as well.
        """
        global config_window
        msg = QMessageBox()
        self.config['SETTINGS']['db_path'] = self.path_to_db.text()
        self.config['SETTINGS']['db_file'] = self.database_file_name.text()
        try:
            new_port = int(self.port.text())
        except ValueError:
            msg.warning(
                self,
                'Ошибка',
                'Порт должен быть числом!'
            )
        else:
            self.config['SETTINGS']['listen_address'] = self.ip.text()
            if 1023 < new_port < 65536:
                self.config['SETTINGS']['default_port'] = str(new_port)
                cwd = os.getcwd()
                cwd = os.path.join(cwd, '..')
                with open(f'{cwd}/server_config.ini', 'w') as conf:
                    self.config.write(conf)
                    msg.information(
                        self,
                        'Успех',
                        'Настройки сохранены!'
                    )
            else:
                msg.warning(
                    self,
                    'Ошибка!',
                    'Порт должен быть в пределах от 1024 до 65536!'
                )
