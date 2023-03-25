import json
import socket

MAX_SIZE = 8 * 1024  # 8KB

class Packet:
	def __init__(self, agency, name, last_name, document, birthday, number_bet, max_size=MAX_SIZE):
		self.max_size = max_size
		self.msg = f"{agency},{name},{last_name},{document},{birthday},{number_bet}"
		self.agency = agency
		self.name = name
		self.last_name = last_name
		self.birthday = birthday
		self.dni = document
		self.number_bet = number_bet

	def encode(self):
		parts = [self.msg[i:i + self.max_size] for i in range(0, len(self.msg), self.max_size)]
		return parts

	def decode(data):
		data_arr = data.split(",")
		agency = data_arr[0]
		name = data_arr[1]
		last_name = data_arr[2]
		document = data_arr[3]
		birthday = data_arr[4]
		number_bet = data_arr[5]

		return Packet(agency, name, last_name, document, birthday, number_bet)

	def size_packet(self):
		return len(self.msg)

	def parts_packet(self):
		return [self.msg[i:i + self.max_size] for i in range(0, len(self.msg), self.max_size)]

	def __str__(self):
		return f"{self.msg}"

class Communication:
	def __init__(self, socket, max_size=MAX_SIZE):
		self.socket = socket
		self.max_size = max_size

	def getpeername(self):
		return self.socket.getpeername()

	def __gen_size_parts(self, a, b):
		if b >= a: return [a]
		fractions = []
		while a > 0:
			amount = min(a, b)
			fractions.append(amount)
			a -= amount
		return fractions

	def send_bet(self, packet):
		size_pkt = packet.size_packet()
		
		"""
		socket.sendall is a high-level Python-only method that sends the entire
		buffer you pass or throws an exception. It does that by calling
		socket.send until everything has been sent or an error occurs.
		"""
		self.socket.sendall(size_pkt.to_bytes(4, byteorder='big'))
		parts = packet.parts_packet()
		for part in parts:
			self.socket.sendall(bytes(part, 'utf-8'))

	def recv_bet(self):
		msg = ""
		
		data = self.socket.recv(4)
		size_pkt = int.from_bytes(data, byteorder='big')
		size_parts = self.__gen_size_parts(size_pkt, self.max_size)
		for size_part in size_parts:
			partial = self.__recv_all(size_part)
			msg += partial.decode()

		return Packet.decode(msg)

	def __recv_all(self, size_msg):
	    # Se inicializa el buffer para guardar los datos recibidos
	    buffer = bytearray()

	    # Se lee el mensaje en bloques de size_msg hasta que se hayan leído todos los datos
	    while len(buffer) < size_msg:
	        data = self.socket.recv(size_msg)
	        if not data:
	            # Se detectó un cierre inesperado del socket
	            raise ConnectionError("Socket cerrado inesperadamente.")
	        buffer += data

	    # Se devuelve el mensaje completo
	    return bytes(buffer)

	def stop(self):
		"""
        Function to release server resources.

        The server closes the socket file descriptor and 
        logs the action at the start and end of the operation.
        """

		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()