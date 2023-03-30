from multiprocessing import Process
from protocol.protocol import CommunicationServer, close_socket
import socket
import logging

class Accepter:
	def __init__(self, server_addr, communications_queue, max_clients, server_flag):
		self.server_addr = server_addr

		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.bind(server_addr)
		self.server_socket.listen(max_clients)
		self.communications_queue = communications_queue
		self.max_clients = max_clients
		self.server_flag = server_flag

		self.accepter_process = Process(target = self.accepter_loop, args = ())
		self.accepter_process.start()

	def accepter_loop(self):		
		clients = 0
		while not self.server_flag.is_set() and clients <= self.max_clients:
			try:
				logging.info(f'action: accept_connections | result: in_progress | server_addr: {self.server_addr}')
				conn, addr = self.server_socket.accept()
				logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
				client_comm = CommunicationServer(conn)
				clients += 1
				self.communications_queue.put(client_comm)
			except:
				pass

		self.server_socket.close()
