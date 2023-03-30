from multiprocessing import Process, Queue, Pool, Event, Manager
from common.accepter import Accepter
import socket
import logging
import signal
from protocol.protocol import CommunicationServer, close_socket
from common.utils import Bet, store_bets, load_bets, has_won
import sys
from common.request_handler import handle_clients
from common.inform_winners import inform_winners


class Server:
	def __init__(self, port, listen_backlog):
		listen_backlog = 1
		self.max_clients = listen_backlog
		self.port = port
		
		self._server_running = True
		signal.signal(signal.SIGTERM, self.__handle_sigterm)

	def run(self):
		#try:
		server_flag = Event()
		clients_queue = Queue(self.max_clients)
		accepter = Accepter(('', self.port), clients_queue, self.max_clients, server_flag)

		server_flag2 = Event()
		consults_queue = Queue(self.max_clients)
		accepter_consults = Accepter(('', self.port+1), consults_queue, self.max_clients, server_flag2)

		handle_clients(server_flag, clients_queue, self.max_clients)
		winners = self.__make_lottery()
		inform_winners(winners, consults_queue, server_flag2, self.max_clients)
		logging.info(f"action: clients_finished | result: success | msg: All winners we're informed")
		"""except OSError:
			logging.debug(f"action: socket_closed | result: success")
		except AttributeError:
			logging.debug(f"action: communication_closed | result: success")"""

		self.stop()

	def __make_lottery(self):
		winners = []
		bets = list(load_bets())
		for bet in bets:
			if has_won(bet): winners.append(bet)

		logging.info(f'action: sorteo | result: success')
		return winners

	def __handle_sigterm(self, *args):
		logging.info("action: signal_received | result: success | signal: SIGTERM")
		self._server_running = False
		self.stop()

	def stop(self):
		"""for client_comm in self.client_comms:
			logging.debug("action: close_resource | result: in_progress | resource: client_communication")
			if client_comm:
				client_comm.stop()
			logging.info("action: close_resource | result: success | resource: client_communication")
		"""
		#close_socket(self._server_socket, 'server_socket')
		logging.info("action: end_server | result: success")
		sys.exit(0)
