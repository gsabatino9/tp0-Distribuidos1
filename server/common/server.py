import socket
import logging
import signal
from protocol.protocol import CommunicationServer, close_socket
from common.utils import Bet, store_bets
import sys

class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._server_running = True
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

    def run(self):
        self.client_comm = None
        while self._server_running:
            try:
                self.client_comm = self.__accept_new_connection()
                self.__handle_client_connection()
            except:
                logging.debug(f"action: socket_closed | result: success")
    
    def __handle_client_connection(self):
        if not self.client_comm: return
        try:
            msg = self.client_comm.recv_bets()
            addr = self.client_comm.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')   
            self.__process_msg(msg)
        except OSError as e:
            logging.error(
                "action: receive_message | result: fail | error: {e}")
        finally:
            self.client_comm.stop()
   
    def __process_msg(self, msg):
        bet = Bet.payload_to_bet(msg.agency, msg.payload)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        self.client_comm.send_chunk_processed()

    def __accept_new_connection(self):
        if not self._server_running: return None

        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

        comm = CommunicationServer(c)

        return comm

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self._server_running = False
        self.stop()

    def stop(self):
        logging.debug("action: close_resource | result: in_progress | resource: client_communication")
        if self.client_comm:
            self.client_comm.stop()
        logging.info("action: close_resource | result: success | resource: client_communication")

        close_socket(self._server_socket, 'server_socket')
        sys.exit(0)
