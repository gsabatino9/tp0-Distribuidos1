from protocol.communication import Communication
from protocol.message_client import MessageClient
from protocol.message_server import MessageServer

SEND_BET = MessageClient.SEND_BET
SEND_LAST_BET = MessageClient.SEND_LAST_BET
SIZE_HEADER = MessageClient.SIZE_HEADER

class CommunicationServer:
    """
    A class that represents a server-side communication channel.
    """

    def __init__(self, socket):
        """
        Constructs a CommunicationServer object.

        :param socket: The socket object used for communication.
        """
        self.comm = Communication(socket)

    def getpeername(self):
        """
        Returns the remote address to which the socket is connected.
        """
        return self.comm.getpeername()

    def recv_bet(self):
        """
        Receives and decodes a bet message from a client.

        :return: The bet message data if it is valid, else None.
        """
        header, payload = self.__recv_message()
        if header.code == SEND_BET or header.code == SEND_LAST_BET:
            return header.agency, payload.data
        else:
            return None

    def send_bet_processed(self):
        """
        Sends a message indicating that a bet of data has been processed.
        """
        msg = MessageServer.bet_processed_message()
        self.comm.send_message(msg)

    def __recv_message(self):
        """
        Receives a message from the client and decodes it.

        :return: The decoded header and payload of the message.
        """
        header = self.__recv_header()
        payload = self.__recv_payload(header.len)

        return header, payload

    def __recv_header(self):
        """
        Receives a message header from the client and decodes it.

        :return: The decoded header of the message.
        """
        header = self.comm.recv_header(SIZE_HEADER)
        header = MessageClient.decode_header(header)

        return header

    def __recv_payload(self, len_payload):
        """
        Receives a message payload from the client and decodes it.

        :param len_payload: The length of the payload to be received.
        :return: The decoded payload of the message.
        """
        payload = self.comm.recv_payload(len_payload)
        payload = MessageClient.decode_payload(payload)

        return payload

    def stop(self):
        """
        Closes the communication channel.
        """
        self.comm.stop()
