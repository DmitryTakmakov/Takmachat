# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_raw.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(756, 534))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.addContact = QtWidgets.QPushButton(self.centralwidget)
        self.addContact.setGeometry(QtCore.QRect(20, 500, 100, 30))
        self.addContact.setObjectName("addContact")
        self.contactsList = QtWidgets.QListView(self.centralwidget)
        self.contactsList.setGeometry(QtCore.QRect(20, 30, 256, 461))
        self.contactsList.setObjectName("contactsList")
        self.contactsLabel = QtWidgets.QLabel(self.centralwidget)
        self.contactsLabel.setGeometry(QtCore.QRect(20, 10, 131, 17))
        self.contactsLabel.setObjectName("contactsLabel")
        self.deleteContact = QtWidgets.QPushButton(self.centralwidget)
        self.deleteContact.setGeometry(QtCore.QRect(130, 500, 100, 30))
        self.deleteContact.setObjectName("deleteContact")
        self.messageHistory = QtWidgets.QListView(self.centralwidget)
        self.messageHistory.setGeometry(QtCore.QRect(290, 30, 491, 351))
        self.messageHistory.setObjectName("messageHistory")
        self.msgHistoryLbl = QtWidgets.QLabel(self.centralwidget)
        self.msgHistoryLbl.setGeometry(QtCore.QRect(290, 10, 91, 17))
        self.msgHistoryLbl.setObjectName("msgHistoryLbl")
        self.msgInput = QtWidgets.QTextEdit(self.centralwidget)
        self.msgInput.setGeometry(QtCore.QRect(290, 400, 491, 91))
        self.msgInput.setObjectName("msgInput")
        self.inputBoxLbl = QtWidgets.QLabel(self.centralwidget)
        self.inputBoxLbl.setGeometry(QtCore.QRect(290, 380, 131, 17))
        self.inputBoxLbl.setObjectName("inputBoxLbl")
        self.sendBtn = QtWidgets.QPushButton(self.centralwidget)
        self.sendBtn.setGeometry(QtCore.QRect(670, 500, 100, 30))
        self.sendBtn.setObjectName("sendBtn")
        self.cleanBtn = QtWidgets.QPushButton(self.centralwidget)
        self.cleanBtn.setGeometry(QtCore.QRect(290, 500, 100, 30))
        self.cleanBtn.setObjectName("cleanBtn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuExit = QtWidgets.QAction(MainWindow)
        self.menuExit.setObjectName("menuExit")
        self.menuAddContact = QtWidgets.QAction(MainWindow)
        self.menuAddContact.setObjectName("menuAddContact")
        self.menuDelContact = QtWidgets.QAction(MainWindow)
        self.menuDelContact.setObjectName("menuDelContact")
        self.menu.addAction(self.menuExit)
        self.menu_2.addAction(self.menuAddContact)
        self.menu_2.addAction(self.menuDelContact)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainWindow)
        self.cleanBtn.clicked.connect(self.msgInput.clear)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Takmachat alpha"))
        self.addContact.setText(_translate("MainWindow", "Добавить"))
        self.contactsLabel.setText(_translate("MainWindow", "Список контактов"))
        self.deleteContact.setText(_translate("MainWindow", "Удалить"))
        self.msgHistoryLbl.setText(_translate("MainWindow", "Сообщения"))
        self.inputBoxLbl.setText(_translate("MainWindow", "Новое сообщение"))
        self.sendBtn.setText(_translate("MainWindow", "Отправить"))
        self.cleanBtn.setText(_translate("MainWindow", "Очистить"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.menu_2.setTitle(_translate("MainWindow", "Контакты"))
        self.menuExit.setText(_translate("MainWindow", "Выход"))
        self.menuExit.setShortcut(_translate("MainWindow", "Alt+Q"))
        self.menuAddContact.setText(_translate("MainWindow", "Добавить контакт"))
        self.menuAddContact.setShortcut(_translate("MainWindow", "Ctrl+Shift+A"))
        self.menuDelContact.setText(_translate("MainWindow", "Удалить контакт"))
        self.menuDelContact.setShortcut(_translate("MainWindow", "Ctrl+Shift+D"))
