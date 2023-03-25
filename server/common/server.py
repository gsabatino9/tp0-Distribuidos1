import socket
import logging
import signal
from protocol.protocol import Packet, Communication
from common.utils import Bet, store_bets

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        # Register signal handler for SIGTERM
        self._server_running = True
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # Server terminates when it receives SIGTERM
        while self._server_running:
            client_comm = self.__accept_new_connection()
            self.__handle_client_connection(client_comm)

    def __handle_client_connection(self, client_comm):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        if not client_comm: return
        try:
            msg = client_comm.recv_bet()
            addr = client_comm.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')   
            self.__process_msg(msg)
        except OSError as e:
            logging.error(
                "action: receive_message | result: fail | error: {e}")
        finally:
            client_comm.stop()
   
    def __process_msg(self, msg):
        bet = Bet(msg.agency, msg.name, msg.last_name, msg.dni, msg.birthday, msg.number_bet)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: {msg.dni} | numero: {msg.number_bet}')

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        if not self._server_running: return None
        # Connection arrived
        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

            comm = Communication(c)
        except OSError:
            comm = None

        return comm

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self._server_running = False
        self.stop()

    def stop(self):
        """
        Function to release server resources.

        The server closes the socket file descriptor and 
        logs the action at the start and end of the operation.
        """

        logging.debug("action: close_resource | result: in_progress | resource: socket")
        try:
            self._server_socket.shutdown(socket.SHUT_RDWR)
            self._server_socket.close()
        except OSError:
            # if socket was alredy closed:
            logging.debug(
                "action: close_resource | result: success | resource: socket | msg: socket already closed")
        finally:
            logging.info("action: close_resource | result: success | resource: socket")
