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

        self.max_clients = listen_backlog

    def run(self):
        self.client_comm = None
        clients_done = 0

        while self._server_running and clients_done < self.max_clients:
            try:
                self.client_comm = self.__accept_new_connection()
                self.__handle_client_connection()
            except:
                logging.debug(f"action: socket_closed | result: success")
            finally:
                clients_done += 1

        logging.info(f"action: clients_finished | result: success | msg: All bets processed")
        self.stop()
    
    def __handle_client_connection(self):
        if not self.client_comm: return
        self.__recv_all_bets()
        self.client_comm.stop()
   
    def __recv_all_bets(self):
        logging.info('action: esperando_chunk')
        msg = self.client_comm.recv_bets()

        addr = self.client_comm.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]}')   
        self.__process_msg(msg)

        while not self.client_comm.is_last_chunk(msg):
            logging.info('action: esperando_chunk')
            msg = self.client_comm.recv_bets()

            addr = self.client_comm.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]}')   
            self.__process_msg(msg)

        logging.info(f'action: all_bets_processed | result: success | agency: {msg.agency}')   

    def __process_msg(self, msg):
        bets = Bet.payload_to_bets(msg.agency, msg.payload)
        store_bets(bets)
        logging.info(f'action: apuestas_almacenadas | result: success | agencia: {msg.agency} | cantidad: {len(bets)}')
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
