"""
GUI for deleting an existing client.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QComboBox


class DelContactDialog(QDialog):
    """
    Main class of GUI.
    """

    def __init__(self, db):
        """
        GUI initialization

        :param db: client's database.
        """
        super().__init__()
        self.db = db

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для удаления.')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.cntct_selector_label = QLabel(
            'Выберите контакт для удаления: ',
            self
        )
        self.cntct_selector_label.setFixedSize(250, 20)
        self.cntct_selector_label.move(10, 0)

        self.cntct_selector = QComboBox(self)
        self.cntct_selector.setFixedSize(200, 20)
        self.cntct_selector.move(10, 30)

        self.ok_btn = QPushButton('Удалить', self)
        self.ok_btn.setFixedSize(100, 30)
        self.ok_btn.move(230, 20)

        self.cncl_btn = QPushButton('Отмена', self)
        self.cncl_btn.setFixedSize(100, 30)
        self.cncl_btn.move(230, 60)
        self.cncl_btn.clicked.connect(self.close)

        self.cntct_selector.addItems(sorted(self.db.get_contacts()))
