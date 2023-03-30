import socket
import logging
import signal
from protocol.protocol import CommunicationClient
import sys
from time import sleep

def str_to_address(server_addr):
    list_aux = server_addr.split(':')
    list_aux[1] = int(list_aux[1])

    return tuple(list_aux)

class Client:
    def __init__(self, client_id, server_addr):
        self._client_id = client_id
        self._server_addr = str_to_address(server_addr)
        self.comm = self.__create_connection()

        signal.siginterrupt(signal.SIGTERM, True)
        signal.signal(signal.SIGTERM, self.__handle_sigterm)
        self.running = True

    def send_bet(self, name, last_name, document, birthday, number_bet):
        #sleep(3)
        payload = [f"{name},{last_name},{document},{birthday},{number_bet}"]
        try:
            self.comm.send_bets(payload, self._client_id, is_last=True)
            status = self.comm.recv_status_chunk()
            if status:
                logging.info(f'action: apuesta_enviada | result: success | dni: {document} | numero: {number_bet}')
        except:
            logging.debug(f'action: communication_closed')

        self.stop()

    def __create_connection(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self._server_addr)

        return CommunicationClient(client_socket)

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self.stop()

    def stop(self):
        logging.debug("action: close_resource | result: in_progress | resource: server_communication")
        if self.comm:
            self.comm.stop()
        logging.info("action: close_resource | result: success | resource: server_communication")

        if self.running:
            self.running = False
        
        logging.info("action: end_client_loop | result: success")
        sys.exit(0)
