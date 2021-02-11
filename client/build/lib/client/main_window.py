"""
GUI of main window of client's app.
"""
from base64 import b64encode, b64decode
from json import JSONDecodeError
from logging import getLogger

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, \
    QColor
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QDialog

from client.add_contact import AddContactDialog
from client.del_contact import DelContactDialog
from client.gui import Ui_MainWindow
from utils.constants import MESSAGE_TEXT, SENDER
from utils.errors import ServerError

LOGGER = getLogger('client')


class MainWindowClient(QMainWindow):
    """
    GUI main class.
    """

    def __init__(self,
                 client_db,
                 client_socket,
                 encryption_keys: RsaKey):
        """
        GUI initialization. Sets up all the elements,
        creates attributes needed for the class to function,
        updates the list of active clients and disables the inputs.

        :param client_db: client's database
        :param client_socket: client itself in a form of socket
        :param encryption_keys: pretty self-explanatory :)
        """
        super().__init__()
        self.client_db = client_db
        self.client_socket = client_socket

        self.decrypter = PKCS1_OAEP.new(encryption_keys)

        self.gui = Ui_MainWindow()
        self.gui.setupUi(self)

        self.gui.inputBoxLbl.setFixedSize(491, 17)
        self.gui.menuExit.triggered.connect(qApp.exit)
        self.gui.sendBtn.clicked.connect(self.send_message)
        self.gui.addContact.clicked.connect(self.add_contact_dialog)
        self.gui.menuAddContact.triggered.connect(
            self.add_contact_dialog)
        self.gui.deleteContact.clicked.connect(
            self.del_contact_dialog)
        self.gui.menuDelContact.triggered.connect(
            self.del_contact_dialog)

        self.contacts_model = None
        self.msg_history_model = None
        self.messages = QMessageBox()
        self.current_conv = None
        self.current_conv_key = None
        self.encryptor = None
        self.gui.messageHistory.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.gui.messageHistory.setWordWrap(True)
        self.gui.contactsList.doubleClicked.connect(
            self.active_user_select)

        self.contact_list_update()
        self.disable_input()
        self.show()

    def disable_input(self):
        """
        Disable the input fields in the GUI if the recipient is not selected.
        """
        self.gui.inputBoxLbl.setText('Дважды кликните по имени получателя.')
        self.gui.msgInput.clear()
        if self.msg_history_model:
            self.msg_history_model.clear()

        self.gui.cleanBtn.setDisabled(True)
        self.gui.sendBtn.setDisabled(True)
        self.gui.msgInput.setDisabled(True)

        self.encryptor = None
        self.current_conv = None
        self.current_conv_key = None

    def msg_history_update(self):
        """
        Update the message history of two users.
        Shows only 20 last messages.
        If there are no messages between users, creates an empty model.
        """
        msg_list = sorted(
            self.client_db.get_message_history(self.current_conv),
            key=lambda itm: itm[3]
        )
        if not self.msg_history_model:
            self.msg_history_model = QStandardItemModel()
            self.gui.messageHistory.setModel(self.msg_history_model)
        self.msg_history_model.clear()
        all_msgs = len(msg_list)
        start_idx = 0
        if all_msgs > 20:
            start_idx = all_msgs - 20
        for i in range(start_idx, all_msgs):
            lst_itm = msg_list[i]
            if lst_itm[1] == 'in':
                msg = QStandardItem(
                    f'{lst_itm[3].replace(microsecond=0)}:\n'
                    f'{lst_itm[2]}'
                )
                msg.setEditable(False)
                msg.setBackground(QBrush(QColor(255, 150, 150)))
                msg.setTextAlignment(Qt.AlignLeft)
                self.msg_history_model.appendRow(msg)
            else:
                msg = QStandardItem(
                    f'{lst_itm[3].replace(microsecond=0)}:\n'
                    f'{lst_itm[2]}'
                )
                msg.setEditable(False)
                msg.setBackground(QBrush(QColor(130, 245, 130)))
                msg.setTextAlignment(Qt.AlignRight)
                self.msg_history_model.appendRow(msg)
        self.gui.messageHistory.scrollToBottom()

    def active_user_select(self):
        """
        Changes the current conversation attribute and triggers the active_user_set method
        when a user double-clicks the name of the recipient in the selector field.
        """
        self.current_conv = self.gui.contactsList.currentIndex().data()
        self.active_user_set()

    def active_user_set(self):
        """
        Sets the active user.
        The method tries to receive the public keys of the recipient,
        if there isn't one - triggers a relevant message.
        Otherwise enables the inputs and updates the message history.
        """
        try:
            self.current_conv_key = self.client_socket.request_pub_key(
                self.current_conv)
            LOGGER.debug(
                'Получен открытый ключ для %s' % self.current_conv)
            if self.current_conv_key:
                self.encryptor = PKCS1_OAEP.new(
                    RSA.import_key(self.current_conv_key))
        except (OSError, JSONDecodeError):
            self.current_conv_key = None
            self.encryptor = None
            LOGGER.error(
                'Не удалось получить открытый ключ для %s'
                % self.current_conv
            )

        if not self.current_conv_key:
            self.messages.warning(
                self,
                'Ошибка!',
                'Отсутствует ключ шифрования для выбранного пользователя!'
            )
            return

        self.gui.inputBoxLbl.setText(
            f'Введите сообщение для {self.current_conv}...')
        self.gui.cleanBtn.setDisabled(False)
        self.gui.sendBtn.setDisabled(False)
        self.gui.msgInput.setDisabled(False)

        self.msg_history_update()

    def contact_list_update(self):
        """
        Updates the contact list.
        Queries the DB and then creates a model with the contacts.
        """
        cntcts = self.client_db.get_contacts()
        self.contacts_model = QStandardItemModel()
        for cnt in sorted(cntcts):
            itm = QStandardItem(cnt)
            itm.setEditable(False)
            self.contacts_model.appendRow(itm)
        self.gui.contactsList.setModel(self.contacts_model)

    def add_contact_dialog(self):
        """
        Calls a modal window to initiate an add-to-contacts dialog.
        Connects the click on 'OK' button to the handler.
        """
        global contact_select
        contact_select = AddContactDialog(
            self.client_socket,
            self.client_db
        )
        contact_select.ok_btn.clicked.connect(
            lambda: self.add_contact_handler(contact_select))
        contact_select.show()

    def add_contact_handler(self, gui_item: QDialog):
        """
        Handles the click by calling the actual method to add new user to contacts.

        :param gui_item: modal window
        """
        contact_login = gui_item.cntct_selector.currentText()
        self.add_contact(contact_login)
        gui_item.close()

    def add_contact(self, contact: str):
        """
        Adds user to client's contacts.
        Checks the DB to see if the user is already in contacts,
        updates the contact list and triggers a relevant message.

        :param contact: login
        """
        try:
            self.client_socket.add_new_contact(contact)
        except OSError as e:
            if e.errno:
                self.messages.critical(
                    self,
                    'Ошибка!',
                    'Потеряно соединение с сервером!'
                )
                self.close()
            self.messages.critical(self,
                                   'Ошибка!',
                                   'Таймаут соединения с сервером'
                                   )
        else:
            self.client_db.add_user_to_contacts(contact)
            new_cntct = QStandardItem(contact)
            new_cntct.setEditable(False)
            self.contacts_model.appendRow(new_cntct)
            LOGGER.info('Добавлен контакт: %s' % contact)
            self.messages.information(self,
                                      'Успех!',
                                      'Контакт успешно добавлен.'
                                      )

    def del_contact_dialog(self):
        """
        Calls a modal window to initiate a delete-from-contacts dialog.
        Connects the click on 'OK' button to the handler.
        """
        global contact_remove
        contact_remove = DelContactDialog(self.client_db)
        contact_remove.ok_btn.clicked.connect(
            lambda: self.del_contact_handler(contact_remove))
        contact_remove.show()

    def del_contact_handler(self, gui_item: QDialog):
        """
        Handles the deletion of a user from contacts.
        Checks if this is possible, and triggers a relevant message.
        If the deleted contact is the one the user is currently chatting with,
        closes the chat window and disables the inputs.

        :param gui_item: modal window
        """
        cntct_name = gui_item.cntct_selector.currentText()
        try:
            self.client_socket.remove_contact(cntct_name)
        except OSError as e:
            if e.errno:
                self.messages.critical(
                    self,
                    'Ошибка!',
                    'Потеряно соединение с сервером!'
                )
                self.close()
            self.messages.critical(
                self,
                'Ошибка!',
                'Таймаут соединения с сервером'
            )
        else:
            self.client_db.delete_user_from_contacts(cntct_name)
            self.contact_list_update()
            LOGGER.info('Контакт %s успешно удален.' % cntct_name)
            self.messages.information(self,
                                      'Успех!',
                                      'Контакт успешно удален.'
                                      )
            self.close()
            if cntct_name == self.current_conv:
                self.current_conv = None
                self.disable_input()

    def send_message(self):
        """
        Sends the message from one user to another.
        Clears the input (if nothing has been entered, stops running),
        encrypts the message and sends it. If no errors occur, saves
        the message to the DB, otherwise triggers a relevant message.
        """
        msg_text = self.gui.msgInput.toPlainText()
        self.gui.msgInput.clear()
        if not msg_text:
            return
        msg_text_encrypted = self.encryptor.encrypt(
            msg_text.encode('utf-8')
        )
        msg_text_encrypted_base64 = b64encode(msg_text_encrypted)
        try:
            self.client_socket.create_message(
                self.current_conv,
                msg_text_encrypted_base64.decode('ascii')
            )
        except (ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError):
            self.messages.critical(self,
                                   'Ошибка!',
                                   'Потеряно соединение с сервером!'
                                   )
            self.close()
        except OSError as e:
            if e.errno:
                self.messages.critical(
                    self,
                    'Ошибка!',
                    'Потеряно соединение с сервером!'
                )
                self.close()
            self.messages.critical(self,
                                   'Ошибка!',
                                   'Таймаут соединения с сервером'
                                   )
        except ServerError as e:
            self.messages.critical(self,
                                   'Ошибка!',
                                   e.error_message
                                   )
        else:
            self.client_db.save_message_to_history(self.current_conv,
                                                   'out',
                                                   msg_text
                                                   )
            LOGGER.debug(
                'Отправлено сообщение для %s: %s.' % (
                    self.current_conv,
                    msg_text
                )
            )
            self.msg_history_update()

    @pyqtSlot(dict)
    def new_msg(self, message: dict):
        """
        Receives the signal about a new message from the client's socket.
        Receives the message, decrypts it and if no errors occur, saves it
        to the DB. Otherwise triggers a relevant message. If the user is
        currently conversing with the sender of the message, updates the
        message history, otherwise checks if the sender is added to the
        user's contacts and triggers a relevant message. If the sender is
        not in user's contacts, adds him there, and saves the message to the DB.

        :param message: message dictionary
        """
        encrypted_msg = b64decode(message[MESSAGE_TEXT])
        try:
            decrypted_msg = self.decrypter.decrypt(encrypted_msg)
        except (ValueError, TypeError):
            self.messages.warning(
                self,
                'Ошибка!',
                'Не удалось декодировать сообщение!'
            )
            return
        else:
            self.client_db.save_message_to_history(
                self.current_conv,
                'in',
                decrypted_msg.decode('utf-8')
            )
        sender = message[SENDER]
        if sender == self.current_conv:
            self.msg_history_update()
        else:
            if self.client_db.check_for_contact(sender):
                user_resp = self.messages.question(
                    self,
                    'Новое сообщение',
                    f'Получено новое сообщение от {sender}. '
                    f'Открыть чат с ним?',
                    QMessageBox.Yes,
                    QMessageBox.No
                )
                if user_resp == QMessageBox.Yes:
                    self.current_conv = sender
                    self.active_user_set()
            else:
                user_resp = self.messages.question(
                    self,
                    'Новое сообщение',
                    f'Получено новое сообщение от {sender}. '
                    f'Этого пользователя нет у вас в контактах. '
                    f'Добавить его в контакты и открыть с ним чат?',
                    QMessageBox.Yes,
                    QMessageBox.No
                )
                if user_resp == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_conv = sender
                    self.client_db.save_message_to_history(
                        self.current_conv,
                        'in',
                        decrypted_msg.decode('utf-8')
                    )
                    self.active_user_set()

    @pyqtSlot()
    def connection_lost(self):
        """
        Handles the signal about lost connection from the client's socket.
        """
        self.messages.warning(
            self,
            'Предупреждение!',
            'Непредвиденный сбой. Потеряно соединение с сервером.'
        )
        self.close()

    @pyqtSlot()
    def status_205(self):
        """
        Handles the signal to update the contact list from the client's socket.
        Checks if the current correspondent is still on the server, and
        triggers relevant message if not. Otherwise, updates the contact list.
        """
        if self.current_conv and not self.client_db.check_for_user(
                self.current_conv):
            self.messages.warning(
                self,
                'Ошибка!',
                'К сожалению, данный пользователь отсутствует на сервере.'
            )
            self.disable_input()
            self.current_conv = None
        else:
            self.contact_list_update()

    def establish_connection(self, socket):
        """
        Connects slots to signals, sent by client's socket.

        :param socket: client's socket
        """
        socket.new_msg_signal.connect(self.new_msg)
        socket.connection_lost.connect(self.connection_lost)
        socket.msg_205_signal.connect(self.status_205)
