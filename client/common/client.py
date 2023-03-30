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
        addr = server_addr.split(':')[0]
        port = int(server_addr.split(':')[1])

        self._client_id = client_id
        self._server_addr = str_to_address(server_addr)
        self.comm = self.__create_connection(self._server_addr)
        self.comm_consult = self.__create_connection((addr, port+1))

        signal.siginterrupt(signal.SIGTERM, True)
        signal.signal(signal.SIGTERM, self.__handle_sigterm)
        self.running = True

    def run(self, filepath, chunk_size):
        try:
            self.__send_bets_for_chunks(filepath, chunk_size)
            self.__consult_agency_winners()
        except OSError:
            logging.debug(f'action: communication_closed')

        self.stop()

    def __consult_agency_winners(self):
        self.comm_consult.send_consult_agency_winners(self._client_id)
        winners = self.comm_consult.recv_agency_winners()
        if winners:
            winners = [i for i in winners if len(i) > 2]
            logging.info(f'action: consulta_ganadores | result: success | cant_ganadores: {len(winners)}')
        else:
            logging.error(f'action: consulta_ganadores | result: error')

    def __send_bets_for_chunks(self, filepath, chunk_size):
        with open(filepath) as f:
            reader = csv.reader(f)
            last_chunk = False
            while True:
                chunk = list(islice(reader, chunk_size))
                if not chunk: break

                last_chunk = True if (len(chunk) < chunk_size) else False
                self.__send_bets(chunk, last_chunk)

            if not last_chunk:
                self.__send_bets(list(''), True)
            
    def __send_bets(self, rows, is_last=False):
        #sleep(1)
        payload = construct_payload(rows)
        self.comm.send_bets(payload, self._client_id, is_last=is_last)
        status = self.comm.recv_status_chunk()
        if status:
            logging.info(f'action: apuestas_enviadas | result: success | agencia: {self._client_id} | cantidad: {len(payload)}')

    def __create_connection(self, addr):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(addr)
            return CommunicationClient(client_socket)
        except ConnectionRefusedError:
            self.stop()

    def __handle_sigterm(self, *args):
        logging.info("action: signal_received | result: success | signal: SIGTERM")
        self.stop()

    def stop(self):
        if not self.running: return

        logging.debug("action: close_resource | result: in_progress | resource: server_communication")
        if self.comm:
            self.comm.stop()
        if self.comm_consult:
            self.comm_consult.stop()
        logging.info("action: close_resource | result: success | resource: server_communication")

        if self.running:
            self.running = False
        
        logging.info("action: end_client_loop | result: success")
        sys.exit(0)
