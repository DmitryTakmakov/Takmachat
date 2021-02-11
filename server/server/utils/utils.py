"""
Common functions used in both server and client apps.
"""

import json
from socket import socket
from sys import path

from utils.decorators import function_log
from utils.errors import IncorrectDataReceivedError, NotADictionaryError
from utils.constants import MAX_PACK_LENGTH, DEFAULT_ENCODING

path.append('../')


@function_log
def receive_message(sckt: socket) -> dict:
    """
    Receives messages sent to client's or server's socket,
    checks if the data received has the correct format, decodes bytes into JSON,
    then - to dictionary and returns the dictionary

    :param sckt: receiving socket
    """
    original_response = sckt.recv(MAX_PACK_LENGTH)
    if isinstance(original_response, bytes):
        decoded_response = original_response.decode(DEFAULT_ENCODING)
        response_dict = json.loads(decoded_response)
        if isinstance(response_dict, dict):
            return response_dict
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@function_log
def send_message(sckt: socket, message: dict):
    """
    Sends the messages from the client's or server's socket.
    Checks if the message has the correct format, converts it to JSON, encodes to bytes
    and then sends it.

    :param sckt: sending socket
    :param message: message to be sent
    """
    if not isinstance(message, dict):
        raise NotADictionaryError
    json_message = json.dumps(message)
    encoded_message = json_message.encode(DEFAULT_ENCODING)
    sckt.send(encoded_message)
