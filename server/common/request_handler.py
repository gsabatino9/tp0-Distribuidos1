from multiprocessing import Process, Queue, Pool, Event, Manager
from protocol.protocol import CommunicationServer
from common.utils import Bet, store_bets, load_bets, has_won
import logging

class RequestHandler:
	def __init__(self, communications_queue, server_flag, max_clients):
		self.communications_queue = communications_queue
		self.server_flag = server_flag
		self.max_clients = max_clients

	def run(self):
		clients_finished = 0
		with Manager() as manager:
			lock = manager.Lock()

			with Pool(processes=4) as pool:
				while not self.server_flag.is_set():
					comm = self.communications_queue.get()
					res = pool.apply_async(self.handle_request, (comm, lock))
					comm = res.get()
					if comm:
						self.communications_queue.put(comm)
					else:
						logging.info(f'action: client_finished | result: success')   
						clients_finished += 1

					if clients_finished == self.max_clients:
						self.server_flag.set()

	def handle_request(self, client_comm, lock):
		request = client_comm.recv_msg()
		if client_comm(request).is_chunk():
			self.__process_chunk(request, client_comm, lock)

		elif client_comm(request).is_last_chunk():
			self.__process_chunk(request, client_comm, lock)

		#elif client_comm(request).is_consult_winners():
			# ...

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
