from multiprocessing import Queue, Event
import socket
import logging
import signal
import sys
from protocol.protocol import CommunicationServer, close_socket
from common.accepter import Accepter
from common.utils import has_won, load_bets
from common.request_handler import handle_clients
from common.inform_winners import inform_winners


class Server:
	def __init__(self, server_port, consult_server_port, listen_backlog):
		self.max_clients = listen_backlog
		self.server_port = server_port
		self.consult_server_port = consult_server_port
		
		self._server_running = True
		signal.signal(signal.SIGTERM, self.__handle_sigterm)

	def run(self):
		try:
			stop_bets = Event()
			clients_queue = Queue(self.max_clients)
			accepter = Accepter(('', self.server_port), clients_queue, self.max_clients, stop_bets)

			stop_consults = Event()
			consults_queue = Queue(self.max_clients)
			accepter_consults = Accepter(('', self.consult_server_port), consults_queue, self.max_clients, stop_consults)

			handle_clients(stop_bets, clients_queue, self.max_clients)
			winners = self.__make_lottery()
			inform_winners(winners, consults_queue, stop_consults, self.max_clients)
			logging.info(f"action: clients_finished | result: success | msg: All winners we're informed")
		except OSError:
			logging.debug(f"action: socket_closed | result: success")
		except AttributeError:
			logging.debug(f"action: communication_closed | result: success")

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
		logging.info("action: end_server | result: success")
		sys.exit(0)
