from protocol.communication import Communication
from protocol.message_client import MessageClient
from protocol.message_server import MessageServer

BET_PROCESSED = MessageServer.BET_PROCESSED
SIZE_HEADER = MessageServer.SIZE_HEADER

class CommunicationClient:
    """
    Represents a communication client for sending and receiving messages to/from the server.
    """

    def __init__(self, socket):
        """
        Initializes a new CommunicationClient object.

        Parameters:
        socket (socket): The socket object used for communication.
        """
        self.comm = Communication(socket)

    def getpeername(self):
        """
        Returns the remote address to which the socket is connected.

        Returns:
        (str, int): The remote address to which the socket is connected.
        """
        return self.comm.getpeername()

    def send_bet(self, bets, agency, is_last=False):
        """
        Sends a bet to the server.

        Parameters:
        bets (list): A list of bets to send.
        agency (int): The agency code that the bets are associated with.
        is_last (bool): A boolean indicating whether this is the last bet to be sent.
        """
        msg = MessageClient.bet_message(agency, bets, is_last)
        self.comm.send_message(msg)

    def recv_status_bet(self):
        """
        Receives a message from the server indicating whether a bet has been processed.

        Returns:
        bool: A boolean indicating whether the bet has been processed.
        """
        header, payload = self.__recv_message()
        if header.code == BET_PROCESSED:
            return True
        else:
            return False

    def __recv_message(self):
        """
        Receives a message from the server.

        Returns:
        (namedtuple, namedtuple): A named tuple representing the header of the message and a named tuple representing
        the payload of the message.
        """
        header = self.__recv_header()
        payload = self.__recv_payload(header.len)

        return header, payload

    def __recv_header(self):
        """
        Receives the header of a message from the server.

        Returns:
        namedtuple: A named tuple representing the header of the message.
        """
        header = self.comm.recv_header(SIZE_HEADER)
        header = MessageServer.decode_header(header)

        return header

    def __recv_payload(self, len_payload):
        """
        Receives the payload of a message from the server.

        Parameters:
        len_payload (int): The length of the payload to receive.

        Returns:
        namedtuple: A named tuple representing the payload of the message.
        """
        payload = self.comm.recv_payload(len_payload)
        payload = MessageServer.decode_payload(payload)

        return payload

    def stop(self):
        """
        Closes the connection with the server.
        """
        self.comm.stop()
