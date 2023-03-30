import socket
import logging
import signal
from protocol.protocol import CommunicationClient
import sys
from time import sleep
from common.utils import str_to_address, construct_payload
import csv
from itertools import islice

class Client:
    def __init__(self, client_id, server_addr):
        self._client_id = client_id
        self._server_addr = str_to_address(server_addr)
        self.comm = self.__create_connection()

        signal.siginterrupt(signal.SIGTERM, True)
        signal.signal(signal.SIGTERM, self.__handle_sigterm)
        self.running = True

    def send_bets_for_chunks(self, filepath, chunk_size):
        with open(filepath) as f:
            reader = csv.reader(f)
            try:
                last_chunk = False
                while True:
                    chunk = list(islice(reader, chunk_size))
                    if not chunk: break

                    last_chunk = True if (len(chunk) < chunk_size) else False
                    self.send_bets(chunk, last_chunk)

                if not last_chunk:
                    self.send_bets(list(''), True)
            except:
                logging.debug(f'action: communication_closed')

        self.stop()

    def send_bets(self, rows, is_last=False):
        #sleep(3)
        payload = construct_payload(rows)
        self.comm.send_bets(payload, self._client_id, is_last=is_last)
        logging.info(f'action: esperando_recv_status')
        status = self.comm.recv_status_chunk()
        if status:
            logging.info(f'action: apuestas_enviadas | result: success | agencia: {self._client_id} | cantidad: {len(payload)}')

    def __create_connection(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(self._server_addr)

        return CommunicationClient(client_socket)

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self.stop()

    def stop(self):
        if not self.running: return

        logging.debug("action: close_resource | result: in_progress | resource: server_communication")
        if self.comm:
            self.comm.stop()
        logging.info("action: close_resource | result: success | resource: server_communication")

        if self.running:
            self.running = False
        
        logging.info("action: end_client_loop | result: success")
        sys.exit(0)
