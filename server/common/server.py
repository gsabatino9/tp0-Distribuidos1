import socket
import logging
import signal
from protocol.protocol import CommunicationServer
from common.utils import Bet, store_bets

def payload_to_bet(agency, payload):
    data = payload.split(',')
    name = data[0]
    last_name = data[1]
    document = data[2]
    birthday = data[3]
    number_bet = data[4]

    return Bet(agency, name, last_name, document, birthday, number_bet)

class Server:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._server_running = True
        signal.signal(signal.SIGTERM, self.__handle_sigterm)

    def run(self):
        while self._server_running:
            client_comm = self.__accept_new_connection()
            self.__handle_client_connection(client_comm)

    def __handle_client_connection(self, client_comm):
        if not client_comm: return
        try:
            msg = client_comm.recv_bets()
            addr = client_comm.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')   
            self.__process_msg(client_comm, msg)
        except OSError as e:
            logging.error(
                "action: receive_message | result: fail | error: {e}")
        finally:
            client_comm.stop()
   
    def __process_msg(self, client_comm, msg):
        bet = payload_to_bet(msg.data["agency"], msg.data["payload"][0])
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        client_comm.send_chunk_processed()

    def __accept_new_connection(self):
        if not self._server_running: return None

        try:
            logging.info('action: accept_connections | result: in_progress')
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

            comm = CommunicationServer(c)
        except OSError:
            comm = None

        return comm

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self._server_running = False
        self.stop()

    def stop(self):
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
