from multiprocessing import Process, Queue, Pool, Event, Manager
from common.accepter import Accepter
import socket
import logging
import signal
from protocol.protocol import CommunicationServer, close_socket
from common.utils import Bet, store_bets, load_bets, has_won
import sys
from common.request_handler import RequestHandler

POOL_SIZE = 1

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
		winners_queue = Queue(1)
		consults_queue = Queue(self.max_clients)
		#request_handler = RequestHandler(clients_queue, server_flag, self.max_clients)

		#request_handler.run()

		clients_finished = 0
		with Manager() as manager:
			lock = manager.Lock()

			with Pool(processes=POOL_SIZE) as pool:
				while not server_flag.is_set():
					comm = clients_queue.get()
					res = pool.apply_async(self.handle_request, (comm, lock))
					comm = res.get()
					if comm:
						clients_queue.put(comm)
					else:
						logging.info(f'action: client_finished | result: success')   
						clients_finished += 1

					if clients_finished == self.max_clients:
						server_flag.set()

		self.__make_lottery(winners_queue)
		logging.info(f"action: clients_finished | result: success | msg: All winners we're informed")
		"""except OSError:
			logging.debug(f"action: socket_closed | result: success")
		except AttributeError:
			logging.debug(f"action: communication_closed | result: success")"""

		self.stop()

	def handle_request(self, client_comm, lock):
		request = client_comm.recv_msg()
		if client_comm.is_chunk(request):
			return self.__process_chunk(request, client_comm, lock)

		elif client_comm.is_last_chunk(request):
			client_comm = self.__process_chunk(request, client_comm, lock)
			logging.info('Cliente terminó')
			return None

		#elif client_comm.is_consult_winners(request):
		#	consults_queue.put(client_comm)
		#	return None

		#else:
			# spawneo algún error

	def __process_chunk(self, request, client_comm, lock):
		#if not self._server_running: return
		msg = client_comm.recv_bets(request)
		bets = Bet.payload_to_bets(msg.agency, msg.payload)
		with lock:
			store_bets(bets)
		logging.info(f'action: apuestas_almacenadas | result: success | agencia: {msg.agency} | cantidad: {len(bets)}')
		client_comm.send_chunk_processed()

		return client_comm

	def __make_lottery(self, winners_queue):
		winners = []
		bets = list(load_bets())
		for bet in bets:
			if has_won(bet): winners.append(bet)

		logging.info(f'action: sorteo | result: success')

		winners_queue.put(winners)

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
