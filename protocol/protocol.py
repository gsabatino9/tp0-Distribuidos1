import json
import socket
import logging

MAX_SIZE = (8 * 1024) - 128

def close_socket(socket_to_close, resource_str):
    logging.debug(f"action: close_resource | result: in_progress | resource: {resource_str}")
    try:
        socket_to_close.shutdown(socket.SHUT_RDWR)
        socket_to_close.close()
    except OSError:
        # if socket was alredy closed:
        logging.debug(
            f"action: close_resource | result: success | resource: {resource_str} | msg: socket already closed")
    finally:
        logging.info(f"action: close_resource | result: success | resource: {resource_str}")

class Message:
	def __init__(self, data_json, ensure_ascii=True):
		self.msg = json.dumps(data_json, ensure_ascii=ensure_ascii)
		self.data = data_json
		self.type_message = int(data_json["type_message"])

	def encode(self, max_size=MAX_SIZE):
		chunks = [self.msg[i:i + max_size] for i in range(0, len(self.msg), max_size)]
		return chunks

	@classmethod
	def message_agency(cls, type_message, agency, payload=None):
		data_json = {"type_message": type_message, "agency": agency, "payload": payload}
		return cls(data_json)

	@classmethod
	def message_server(cls, type_message, payload=None):
		data_json = {"type_message": type_message, "payload": payload}
		return cls(data_json)

	@staticmethod
	def decode(msg):
		data_json = json.loads(msg)
		return Message(data_json, ensure_ascii=False)

	def size_msg(self):
		return len(self.msg)

	def __str__(self):
		return self.msg

class CommunicationClient:
	SEND_CHUNK = 1
	SEND_LAST_CHUNK = 2
	CONSULT_AGENCY_WINNERS = 3

	def __init__(self, socket):
		self.comm = Communication(socket)

	def getpeername(self):
		return self.comm.getpeername()

	def send_bets(self, bets, agency, is_last=False):
		code = self.SEND_LAST_CHUNK if is_last else self.SEND_CHUNK
		msg = Message.message_agency(code, agency, bets)
		self.comm.send_msg(msg)

	def recv_status_chunk(self):
		msg = self.comm.recv_msg()
		if msg.type_message == CommunicationServer.CHUNK_PROCESSED:
			return True
		else:
			return False

	def send_consult_agency_winners(self, agency):
		msg = Message.message_agency(self.CONSULT_AGENCY_WINNERS, agency)
		self.comm.send_msg(msg)

	def recv_agency_winners(self):
		msg = self.comm.recv_msg()
		if msg.type_message == CommunicationServer.INFORM_AGENCY_WINNERS:
			return msg.data["payload"].split(',')
		else:
			return None

	def stop(self):
		self.comm.stop()

class CommunicationServer:
	CHUNK_PROCESSED = 1
	INFORM_AGENCY_WINNERS = 2

	def __init__(self, socket):
		self.comm = Communication(socket)

	def getpeername(self):
		return self.comm.getpeername()

	def recv_bets(self):
		msg = self.comm.recv_msg()
		msg.agency = msg.data["agency"]
		msg.payload = msg.data["payload"]

		return msg

	def is_last_chunk(self, msg):
		return msg.type_message == CommunicationClient.SEND_LAST_CHUNK

	def send_chunk_processed(self):
		msg = Message.message_server(self.CHUNK_PROCESSED)
		self.comm.send_msg(msg)

	def send_agency_winners(self, winners):
		winners = ','.join(winners)
		msg = Message.message_server(self.INFORM_AGENCY_WINNERS, payload=winners)
		self.comm.send_msg(msg)

	def recv_consult_winners(self):
		msg = self.comm.recv_msg()
		if msg.type_message == CommunicationClient.CONSULT_AGENCY_WINNERS:
			return int(msg.data["agency"])
		else:
			return None

	def stop(self):
		self.comm.stop()
		
class Communication:
	def __init__(self, socket, max_size=MAX_SIZE):
		self.socket = socket
		self.max_size = max_size

	def getpeername(self):
		return self.socket.getpeername()

	def send_msg(self, msg):
		size_to_send = msg.size_msg()

		self.socket.sendall(size_to_send.to_bytes(4, byteorder='big'))
		parts = msg.encode()
		for part in parts:
			self.socket.sendall(bytes(part, 'utf-8'))

	def recv_msg(self):
		msg = ""

		data = self.socket.recv(4)
		if not data: return None
		size_msg = int.from_bytes(data, byteorder='big')

		size_parts = self.__obtain_parts(size_msg)
		for size_part in size_parts:
			partial = self.__recv_all(size_part)
			msg += partial.decode()

		return Message.decode(msg)

	def __obtain_parts(self, size_msg):
		if size_msg <= self.max_size: return [size_msg]
		parts = []
		tmp = 0
		while tmp != size_msg:
			aug = min(self.max_size, size_msg-tmp)
			parts.append(aug)
			tmp += aug
			
		return parts

	def __recv_all(self, size_msg):
		buffer = bytearray()

		while len(buffer) < size_msg:
			data = self.socket.recv(size_msg-len(buffer))
			if not data:
				raise ConnectionError("Socket cerrado inesperadamente.")
			buffer += data

		return bytes(buffer)

	def stop(self):
		close_socket(self.socket, 'communication_socket')