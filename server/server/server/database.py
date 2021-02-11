"""
Server's database module.
"""
import sys
from datetime import datetime

from Crypto.PublicKey.RSA import RsaKey
from sqlalchemy import create_engine, MetaData, Table, Column, \
    Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator

sys.path.append('../')


class ServerDatabase:
    """
    Representation of the server's database.
    """

    class AllUsers:
        """
        Representation class for table of all users.
        """

        def __init__(self,
                     username: str,
                     password_hash: bytes):
            """
            Initialization of the table.

            :param username: client's login
            :param password_hash: hashed password
            """
            self.id = None
            self.login = username
            self.password_hash = password_hash
            self.public_key = None
            self.last_login = datetime.now()

        def __repr__(self):
            """
            Representation for print.
            """
            return "<User ('%s')>" % self.login

    class UserLoginHistory:
        """
        Representation class for table with users' login history.
        """

        def __init__(self,
                     login: str,
                     address: str,
                     port: int,
                     date: datetime):
            """
            Initialization of the table.

            :param login: client's nickname
            :param address: client's IP address
            :param port: client's port
            :param date: date and time of activity
            """
            self.id = None
            self.user = login
            self.ip_address = address
            self.port = port
            self.last_active = date

        def __repr__(self):
            """
            Representation for print.
            """
            return "<UserLoginHistory ('%s') ('%s')>" % (
                self.user, self.last_active)

    class ActiveUsers:
        """
        Representation class for table of active clients.
        """

        def __init__(self,
                     login: str,
                     address: str,
                     port: int,
                     date: datetime):
            """
            Initialization of table.

            :param login: client's nickname
            :param address: client's IP address
            :param port: client's port
            :param date: date and time of activity
            """
            self.id = None
            self.user = login
            self.ip_address = address
            self.port = port
            self.last_active = date

        def __repr__(self):
            """
            Representation for print.
            """
            return "<ActiveUser ('%s') ('%s')>" % (
                self.user, self.last_active)

    class ContactList:
        """
        Representation class for table of users' contacts
        """

        def __init__(self,
                     owner: str,
                     contact: str):
            """
            Initialization of table.

            :param owner: contact owner
            :param contact: contact itself
            """
            self.id = None
            self.contact_owner = owner
            self.contact = contact

        def __repr__(self):
            """
            Representation for print.
            """
            return "<Contact (owner '%s') (contact '%s')>" % (
                self.contact_owner, self.contact)

    class UserActionHistory:
        """
        Representation class for table of users' activities' history
        """

        def __init__(self,
                     login: str):
            """
            Initialization of the table.

            :param login: client's nickname
            """
            self.id = None
            self.user = login
            self.sent_messages = 0
            self.received_messages = 0

        def __repr__(self):
            """
            Representation for print.
            """
            return "<ActionHistory (user '%s') (sent '%s') (received '%s')>" % (
                       self.user,
                       self.sent_messages,
                       self.received_messages
                   )

    def __init__(self, filepath: str):
        """
        Initialization and creation of tables.
        Creates all the tables, mappers and a session.
        Deletes all previous entries from the table of active users.

        :param filepath: path to DB
        """
        self.engine = create_engine(
            f'sqlite:///{filepath}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.metadata = MetaData()
        all_users_table = Table(
            'all_users',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('login', String(25), unique=True),
            Column('password_hash', String(128)),
            Column('public_key', Text),
            Column('last_login', DateTime)
        )
        user_login_history_table = Table(
            'user_login_history',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('all_users.login')),
            Column('ip_address', String(16)),
            Column('port', String(5)),
            Column('last_active', DateTime)
        )
        active_users_table = Table(
            'active_users',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('all_users.login'), unique=True),
            Column('ip_address', String(16)),
            Column('port', String(5)),
            Column('last_active', DateTime)
        )
        user_contacts_table = Table(
            'user_contacts',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('contact_owner', ForeignKey('all_users.login')),
            Column('contact', ForeignKey('all_users.login'))
        )
        user_message_history_table = Table(
            'user_action_history',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('all_users.login')),
            Column('sent_messages', Integer),
            Column('received_messages', Integer)
        )

        self.metadata.create_all(self.engine)
        mapper(self.AllUsers, all_users_table)
        mapper(self.UserLoginHistory, user_login_history_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.ContactList, user_contacts_table)
        mapper(self.UserActionHistory, user_message_history_table)

        Sesh = sessionmaker(bind=self.engine)
        self.session = Sesh()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def login_user(self, login: str, ip: str, port: int, key: RsaKey):
        """
        Handles the login process for clients.
        Checks if user is already registered on the server,
        and if he is logs him in, adds him to the table of active
        users and makes a new entry to the login history table.

        :param login: client's nickname
        :param ip: client's IP address
        :param port: client's port
        :param key: client's public RSA key
        """
        qry = self.session.query(self.AllUsers).filter_by(
            login=login)
        if qry.count():
            existing_user = qry.first()
            existing_user.last_login = datetime.now()
            if existing_user.public_key != key:
                existing_user.public_key = key
        else:
            raise ValueError('Пользователь не зарегистрирован')
        new_active_user = self.ActiveUsers(
            login,
            ip,
            port,
            datetime.now()
        )
        self.session.add(new_active_user)
        user_history_entry = self.UserLoginHistory(
            login,
            ip,
            port,
            datetime.now()
        )
        self.session.add(user_history_entry)
        self.session.commit()

    def register_user(self, login: str, pwd_hash: bytes):
        """
        Handles the registration of a new user on the server.
        Creates a new entry to the All Users table and User Action History table.

        :param login: client's nickname
        :param pwd_hash: hashed password
        """
        new_user = self.AllUsers(login, pwd_hash)
        self.session.add(new_user)
        self.session.commit()
        user_history_entry = self.UserActionHistory(new_user.login)
        self.session.add(user_history_entry)
        self.session.commit()

    def remove_user_from_db(self, login: str):
        """
        Removes the user and entries related to him from all the tables!
        ALL OF THEM!

        :param login: client's nickname
        """
        user = self.session.query(self.AllUsers).filter_by(
            login=login).first()
        self.session.query(self.ActiveUsers).filter_by(
            user=user.login).delete()
        self.session.query(self.UserLoginHistory).filter_by(
            user=user.login).delete()
        self.session.query(self.UserActionHistory).filter_by(
            user=user.login).delete()
        self.session.query(self.ContactList).filter_by(
            contact_owner=user.login).delete()
        self.session.query(self.ContactList).filter_by(
            contact=user.login).delete()
        self.session.query(self.AllUsers).filter_by(
            login=login).delete()
        self.session.commit()

    def logout_user(self, login: str):
        """
        Handles the logout process on the server.
        Deletes the user from the table of active users.

        :param login: client's nickname
        """
        leaving_user = self.session.query(self.AllUsers).filter_by(
            login=login).first()
        self.session.query(self.ActiveUsers).filter_by(
            user=leaving_user.login).delete()
        self.session.commit()

    def get_user_pwd_hash(self, login: str) -> bytes:
        """
        Returns the hashed password of the user.

        :param login: client's nickname
        """
        user = self.session.query(self.AllUsers).filter_by(
            login=login).first()
        return user.password_hash

    def get_user_public_key(self, login: str) -> RsaKey:
        """
        Returns the public RSA key of the user.

        :param login: client's nickname
        """
        user = self.session.query(self.AllUsers).filter_by(
            login=login).first()
        return user.public_key

    def check_existing_user(self, login: str) -> bool:
        """
        Checks if such user already exists on the server.
        Returns True if they do, False otherwise.

        :param login: client's nickname
        """
        if self.session.query(self.AllUsers).filter_by(
                login=login).count():
            return True
        else:
            return False

    def add_contact_to_list(self, owner: str, contact: str):
        """
        Handles adding one user to the contacts of another.
        Checks if the user is already in the contact list and finishes
        working if they do, otherwise adds new entry to the Contacts table.

        :param owner: the owner of the contact
        :param contact: user to be added to contact list
        """
        existing_contact = self.session.query(
            self.ContactList).filter_by(
            contact_owner=owner,
            contact=contact
        )
        if existing_contact.count():
            print('Этот пользователь уже у вас в контактах.')
            return
        else:
            new_contact = self.ContactList(owner, contact)
            self.session.add(new_contact)
            self.session.commit()

    def remove_contact_from_list(self, owner: str, contact: str):
        """
        Handles the removal of one user from the contacts of another.
        Checks if the user is actually in the contact list and finishes
        working if they aren't, otherwise deletes the entry from the Contacts table.

        :param owner: the owner of the contact
        :param contact: user to be removed from the contact list
        """
        existing_contact = self.session.query(
            self.ContactList).filter_by(
            contact_owner=owner,
            contact=contact
        ).first()
        if not existing_contact:
            print('Такого пользователя у вас в контактах нет.')
            return
        else:
            self.session.query(self.ContactList).filter_by(
                contact_owner=owner,
                contact=contact
            ).delete()
            self.session.commit()

    def all_users_list(self) -> list:
        """
        Returns the list of tuples with entries of all existing users.
        """
        qry = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_login
        )
        return qry.all()

    def all_active_users_list(self) -> list:
        """
        Returns the list of tuples with entries of all currently active users.
        """
        qry = self.session.query(
            self.AllUsers.login,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.last_active
        ).join(self.AllUsers)
        return qry.all()

    def show_user_login_history(self, user: str = None) -> list:
        """
        Returns the list of tuples with login history of either all users or one specific user.

        :param user: client's nickname
        """
        qry = self.session.query(
            self.AllUsers.login,
            self.UserLoginHistory.ip_address,
            self.UserLoginHistory.port,
            self.UserLoginHistory.last_active
        ).join(self.AllUsers)
        if user:
            qry = qry.filter(self.AllUsers.login == user)
        return qry.all()

    def get_user_contact_list(self, user: str) -> list:
        """
        Returns the list of strings with nicknames of all the contacts of a
        specific user.

        :param user: client's nickname
        """
        client = self.session.query(self.AllUsers).filter_by(
            login=user).one()
        qry = self.session.query(
            self.ContactList,
            self.AllUsers.login
        ).filter_by(contact_owner=client.login).join(
            self.AllUsers,
            self.ContactList.contact == self.AllUsers.login
        )
        return [contact[1] for contact in qry.all()]

    def record_message_to_history(self, sender: str, recipient: str):
        """
        Records message to message history.

        :param sender: self-explanatory
        :param recipient: self-explanatory as well
        """
        sender = self.session.query(self.AllUsers).filter_by(
            login=sender).first().login
        recipient = self.session.query(self.AllUsers).filter_by(
            login=recipient).first().login
        sender_entry = self.session.query(
            self.UserActionHistory).filter_by(user=sender).first()
        sender_entry.sent_messages += 1
        recipient_entry = self.session.query(
            self.UserActionHistory).filter_by(user=recipient).first()
        recipient_entry.received_messages += 1
        self.session.commit()

    def get_message_history(self) -> list:
        """
        Returns the list of tuples with entries of users' message history.
        """
        qry = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_login,
            self.UserActionHistory.sent_messages,
            self.UserActionHistory.received_messages
        ).join(self.AllUsers)
        return qry.all()
