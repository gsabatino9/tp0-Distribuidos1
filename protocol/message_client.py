from collections import namedtuple
from struct import pack, unpack, calcsize

class MessageClient:
	# Constants for message types
	SEND_BET = 1
	SEND_LAST_BET = 2

	# Struct format for message header
	HEADER_CODE = '!BBI'
	# Size of header in bytes
	SIZE_HEADER = calcsize(HEADER_CODE)

	# Define the named tuples used in the protocol
	Header = namedtuple('Header', 'code agency len')
	Payload = namedtuple('Payload', 'data')

	def __init__(self, code, agency, payload=None):
		"""
		Create a new MessageClient instance with the given code, agency, and payload.

		Args:
			code (int): The code for the type of message.
			agency (int): The agency to which the message is addressed.
			payload (list[str], optional): A list of strings to be sent as the message payload.

		Returns:
			A new MessageClient instance.
		"""
		if payload is None:
			payload = []
		payload_bytes = self._pack_payload(payload)

		self.header = self.Header(code, agency, len(payload_bytes))
		self.payload = self.Payload(payload_bytes)

	def encode(self):
		"""
		Encode the message as bytes to be sent over the network.

		Returns:
			bytes: The encoded message as bytes.
		"""
		header = pack(self.HEADER_CODE, self.header.code, self.header.agency, self.header.len)
		payload = pack(f'!{self.header.len}s', self.payload.data)

		return header+payload

	@staticmethod
	def decode_header(header):
		"""
		Decode the message header from bytes.

		Args:
			header (bytes): The message header as bytes.

		Returns:
			Header: A named tuple representing the message header.
		"""
		return MessageClient.Header._make(unpack(MessageClient.HEADER_CODE, header))

	@staticmethod
	def decode_payload(payload_bytes):
		"""
		Unpack the message payload from a string of null-separated strings.

		Args:
			payload_bytes (bytes): The packed payload.

		Returns:
			list[str]: A list of strings representing the message payload.
		"""
		return MessageClient._unpack_payload(payload_bytes)

	def _pack_payload(self, payload):
		"""
		Pack the message payload as a string of null-separated strings.

		Args:
			payload (list[str]): A list of strings to be packed.

		Returns:
			bytes: The packed payload as bytes.
		"""
		payload_str = '\0'.join(payload)
		return payload_str.encode('utf-8')

	@staticmethod
	def _unpack_payload(payload_bytes):
		"""
		Unpack the message payload from a string of null-separated strings.

		Args:
			payload_bytes (bytes): The packed payload.

		Returns:
			list[str]: A list of strings representing the message payload.
		"""
		payload = payload_bytes.decode('utf-8').split('\0')
		return MessageClient.Payload(payload)

	@classmethod
	def bet_message(cls, agency, data, is_last=False):
		"""
		Create a new message to send a bet.

		Args:
			agency (int): The agency to which the message is addressed.
			data (list[str]): A list of strings to be sent as the payload.
			is_last (bool, optional): Whether this is the last bet to be sent.

		Returns:
			bytes: The encoded message as bytes.
		"""
		code = cls.SEND_LAST_BET if is_last else cls.SEND_BET

		return cls(code, agency, data).encode()
