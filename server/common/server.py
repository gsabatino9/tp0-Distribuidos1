import socket
import logging
import signal


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        # Register signal handler for SIGTERM
        self._server_running = True
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

        self.client_sock = None

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # Server terminates when it receives SIGTERM
        while self._server_running:
            self.client_sock = self.__accept_new_connection()
            self.__handle_client_connection()

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        if not self.client_sock: return

        try:
            # TODO: Modify the receive to avoid short-reads
            msg = self.client_sock.recv(1024).rstrip().decode('utf-8')
            addr = self.client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            self.client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error(
                "action: receive_message | result: fail | error: {e}")
        finally:
            self.client_sock.close()

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
        except OSError:
            c = None

        return c

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
            if self.client_sock:
                self.client_sock.shutdown(socket.SHUT_RDWR)
                self.client_sock.close()

            self._server_socket.shutdown(socket.SHUT_RDWR)
            self._server_socket.close()
        except OSError:
            # if socket was alredy closed:
            logging.debug(
                "action: close_resource | result: success | resource: socket | msg: socket already closed")
        finally:
            logging.info("action: close_resource | result: success | resource: socket")

        exit(0)
