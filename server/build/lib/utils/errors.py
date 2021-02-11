"""
Custom errors used in the project.
"""


class IncorrectDataReceivedError(Exception):
    """
    Exception raised if the data received was incorrect.
    """

    def __str__(self):
        """
        Representation for print.
        """
        return 'Принято сообщение с данными некорректного типа.'


class NotADictionaryError(Exception):
    """
    Exception raised if the data received was not a dictionary, when it
    was supposed to be a dictionary.
    """

    def __str__(self):
        """
        Representation for print.
        """
        return "В функцию нужно передавать словарь."


class ServerError(Exception):
    """
    Exception raised when the server encounters and error.
    """

    def __init__(self, error_message):
        """
        There can be a custom error text in this exception.

        :param error_message: custom message
        """
        self.error_message = error_message

    def __str__(self):
        """
        Representation for print.
        """
        return self.error_message
