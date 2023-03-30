from common.utils import Bet, store_bets, load_bets, has_won
import logging
from multiprocessing import Process, Queue, Pool, Event, Manager

POOL_SIZE = 4

def handle_clients(server_flag, clients_queue, max_clients):
	clients_finished = 0
	with Manager() as manager:
		lock = manager.Lock()

		with Pool(processes=POOL_SIZE) as pool:
			while not server_flag.is_set():
				comm = clients_queue.get()
				res = pool.apply_async(handle_request, (comm, lock))
				comm = res.get()
				if comm:
					clients_queue.put(comm)
				else:
					logging.info(f'action: client_finished | result: success')   
					clients_finished += 1

				if clients_finished == max_clients:
					server_flag.set()

def handle_request(client_comm, lock):
	request = client_comm.recv_msg()
	if client_comm.is_chunk(request):
		return __process_chunk(request, client_comm, lock)

	elif client_comm.is_last_chunk(request):
		client_comm = __process_chunk(request, client_comm, lock)
		client_comm.stop()
		return None

def __process_chunk(request, client_comm, lock):
	msg = client_comm.recv_bets(request)
	bets = Bet.payload_to_bets(msg.agency, msg.payload)
	with lock:
		store_bets(bets)
	logging.info(f'action: apuestas_almacenadas | result: success | agencia: {msg.agency} | cantidad: {len(bets)}')
	client_comm.send_chunk_processed()

	return client_comm