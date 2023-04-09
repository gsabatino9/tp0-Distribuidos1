import socket

MAX_SIZE = (8 * 1024) - 128

class Communication:
	def __init__(self, socket, max_size=MAX_SIZE):
		self.socket = socket
		self.max_size = max_size

	def getpeername(self):
		return self.socket.getpeername()

	def send_message(self, msg):
		chunks = [msg[i:i + self.max_size] for i in range(0, len(msg), self.max_size)]
		for part in chunks:
			self.socket.sendall(part)

	def __obtain_parts(self, size_msg):
		if size_msg <= self.max_size: return [size_msg]
		parts = []
		tmp = 0
		while tmp != size_msg:
			aug = min(max_size, size_msg-tmp)
			parts.append(aug)
			tmp += aug
			
		return parts

	def recv_header(self, len_header):
		header_bytes = self.socket.recv(len_header)
		return header_bytes

	def recv_payload(self, len_payload):
		msg = b""
		size_parts = self.__obtain_parts(len_payload)
		for size_part in size_parts:
			partial = self.__recv_all(size_part)
			msg += partial

		return msg

	def __recv_all(self, len_msg):
		buffer = bytearray()

		while len(buffer) < len_msg:
			data = self.socket.recv(len_msg-len(buffer))
			if not data:
				raise ConnectionError("Socket cerrado inesperadamente.")
			buffer += data

		return bytes(buffer)

	def stop(self):
		"""
		Function to release server resources.

		The server closes the socket file descriptor and 
		logs the action at the start and end of the operation.
		"""
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
		except:
			print('Socket ya desconectado')