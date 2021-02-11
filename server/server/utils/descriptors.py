"""
Descriptor for the server port.
"""
from sys import exit as sys_exit
from logging import getLogger

server_logger = getLogger('server')


class Port:
    """
    Descriptor class
    """

    def __set__(self, instance, value):
        """
        Validates the server port.
        """
        if not 1023 < value < 65536:
            server_logger.critical(
                'Вы указали неверное значение порта: %s. '
                'Оно должно быть в диапазоне от 1024 до 65535. '
                'Работа приложения-сервера завершена.' % value
            )
            sys_exit(1)
        else:
            instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        """
        Sets the name of the Port object.
        """
        self.name = name
