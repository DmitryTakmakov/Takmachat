"""
Client's database module.
"""
import os
from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, \
    Integer, String, Text, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.sql import default_comparator


class ClientDatabase:
    """
    Main representation class for a database.
    """

    class ExistingUsers:
        """
        Representation class for a table of existing users.
        """

        def __init__(self, login):
            """
            Initialization method for the table.

            :param login: user's login
            """
            self.id = None
            self.login = login

        def __repr__(self):
            """
            Representation for print.
            """
            return "<User ('%s')>" % self.login

    class MessageHistory:
        """
        Representation class for a table of message history.
        """

        def __init__(self, client, direction, message):
            """
            Initialization method for the table.

            :param client: pretty self-explanatory
            :param direction: the message's direction, could be either 'in' or 'out'
            :param message: the message's text
            """
            self.id = None
            self.client = client
            self.direction = direction
            self.message = message
            self.datetime = datetime.now()

        def __repr__(self):
            """
            Representation for print.
            """
            return "<Message user ('%s') direction ('%s')>" % (
                self.client,
                self.direction
            )

    class Contacts:
        """
        Representation class for a table of user's contacts.
        """

        def __init__(self, contact):
            """
            Initialization method for the table.

            :param contact: contact's login.
            """
            self.id = None
            self.contact = contact

        def __repr__(self):
            """
            Representation for print.
            """
            return "<Contact ('%s')>" % self.contact

    def __init__(self, login):
        """
        Method for initializing the database, creating the tables,
        and establishing the session.

        :param login: client's login
        """
        cwd = os.getcwd()
        file = f'client_{login}.sqlite3'
        self.engine = create_engine(
            f'sqlite:///{os.path.join(cwd, file)}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.metadata = MetaData()

        existing_users_table = Table(
            'existing_users',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('login', String(25), unique=True)
        )

        message_history_table = Table(
            'message_history',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('client', String(25)),
            Column('direction', String(3)),
            Column('message', Text),
            Column('datetime', DateTime)
        )

        contacts_table = Table(
            'contacts',
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('contact', String(25), unique=True)
        )

        self.metadata.create_all(self.engine)
        mapper(self.ExistingUsers, existing_users_table)
        mapper(self.MessageHistory, message_history_table)
        mapper(self.Contacts, contacts_table)
        Sesh = sessionmaker(bind=self.engine)
        self.session = Sesh()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_user_to_contacts(self, login: str):
        """
        Adding user to contacts.
        Queries the DB and if no such login found, adds a new contact.

        :param login: User to be added.
        """
        if not self.session.query(self.Contacts).filter_by(
                contact=login).count():
            new_contact = self.Contacts(login)
            self.session.add(new_contact)
            self.session.commit()

    def delete_user_from_contacts(self, login: str):
        """
        Deleting the user from contacts.
        Queries the DB and deletes the entry (if present).

        :param login: User to be deleted.
        """
        self.session.query(self.Contacts).filter_by(contact=login).delete()

    def add_existing_users(self, users_list: list):
        """
        Update the list of existing users, based on the result returned
        by the server DB.
        First clears the existing table, then adds users from the list.

        :param users_list: the list of users from the server.
        """
        self.session.query(self.ExistingUsers).delete()
        for user in users_list:
            new_user = self.ExistingUsers(user)
            self.session.add(new_user)
        self.session.commit()

    def save_message_to_history(self,
                                client: str,
                                direction: str,
                                message: str):
        """
        Save new message to DB.
        The direction can be either 'in' or 'out', since each client has his own DB.

        :param client: client
        :param direction: message direction
        :param message: message text
        """
        new_message = self.MessageHistory(client, direction, message)
        self.session.add(new_message)
        self.session.commit()

    def get_contacts(self) -> list:
        """
        Return the list of client's contacts.
        """
        return [contact[0] for contact in self.session.query(
            self.Contacts.contact).all()]

    def get_existing_users(self) -> list:
        """
        Return the list of all existing users.
        """
        return [user[0] for user in self.session.query(
            self.ExistingUsers.login).all()]

    def check_for_user(self, login: str) -> bool:
        """
        Check if a user with a given username already exists
        in the table of existing users.
        Returns True if exists, False - if not.

        :param login: user's nickname
        """
        if self.session.query(self.ExistingUsers).filter_by(
                login=login).count():
            return True
        else:
            return False

    def check_for_contact(self, login: str) -> bool:
        """
        Check if a user with a given username already exists
        in the table of user's contacts.
        Returns True if exists, False - if not.

        :param login: user's nickname
        """
        if self.session.query(self.Contacts).filter_by(
                contact=login).count():
            return True
        else:
            return False

    def get_message_history(self, contact: str) -> list:
        """
        Return the message history with a given contact.
        Returns a list of tuples.

        :param contact: sender / recipient
        """
        qry = self.session.query(self.MessageHistory).filter_by(
            client=contact)
        return [(row.client,
                 row.direction,
                 row.message,
                 row.datetime) for row in qry.all()]

    def cleat_contact_list(self):
        """
        Delete all entries in the Contacts table.
        """
        self.session.query(self.Contacts).delete()
