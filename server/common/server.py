import socket
import logging
import signal
from protocol.protocol import CommunicationServer, close_socket
from common.utils import Bet, store_bets, load_bets, has_won
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
		self.client_comms = []
		clients_done = 0
		agencies = {}

		try:
			while self._server_running and clients_done < self.max_clients:
				client_comm = self.__accept_new_connection()
				self.client_comms.append(client_comm)
				self.__handle_client_connection(agencies, client_comm)
			
				clients_done += 1

			self.__make_lottery(agencies)
			logging.info(f"action: clients_finished | result: success | msg: All winners we're informed")
		except OSError:
			logging.debug(f"action: socket_closed | result: success")

		self.stop()
	
	def __handle_client_connection(self, agencies, client_comm):
		if not client_comm: return
		self.__recv_all_bets(client_comm)
		self.__recv_consult_winners(agencies, client_comm)

	def __recv_consult_winners(self, agencies, client_comm):
		agency = client_comm.recv_consult_winners()
		if agency:
			agencies[agency] = client_comm
		else:
			self.stop()

	def __make_lottery(self, agencies):
		bets = list(load_bets())
		logging.info(f'action: sorteo | result: success')
		agencies_winners = {k: [] for k in agencies.keys()}

		for bet in bets:
			if has_won(bet):
				agencies_winners[bet.agency].append(bet.document)

		for agency in agencies_winners.keys():
			client_comm = agencies[agency]
			winners = agencies_winners[agency]
			client_comm.send_agency_winners(winners)

			client_comm.stop()		
   
	def __recv_all_bets(self, client_comm):
		msg = client_comm.recv_bets()

		addr = client_comm.getpeername()
		logging.info(f'action: receive_message | result: success | ip: {addr[0]}')   
		self.__process_msg(msg, client_comm)

		while not client_comm.is_last_chunk(msg):
			msg = client_comm.recv_bets()

			addr = client_comm.getpeername()
			logging.info(f'action: receive_message | result: success | ip: {addr[0]}')   
			self.__process_msg(msg, client_comm)

	def __process_msg(self, msg, client_comm):
		bets = Bet.payload_to_bets(msg.agency, msg.payload)
		store_bets(bets)
		logging.info(f'action: apuestas_almacenadas | result: success | agencia: {msg.agency} | cantidad: {len(bets)}')
		client_comm.send_chunk_processed()

	def __accept_new_connection(self):
		if not self._server_running: return None

		logging.debug('action: accept_connections | result: in_progress')
		c, addr = self._server_socket.accept()
		logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')

		comm = CommunicationServer(c)

		return comm

	def __handle_sigterm(self, *args):
		logging.info("action: signal_received | result: success | signal: SIGTERM")
		self._server_running = False
		self.stop()

	def stop(self):
		for client_comm in self.client_comms:
			logging.debug("action: close_resource | result: in_progress | resource: client_communication")
			if client_comm:
				client_comm.stop()
			logging.info("action: close_resource | result: success | resource: client_communication")

		close_socket(self._server_socket, 'server_socket')
		logging.info("action: end_server | result: success")
		sys.exit(0)
