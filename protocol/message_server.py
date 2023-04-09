from collections import namedtuple
from struct import pack, unpack, calcsize

class MessageServer:
	# Constants for message codes
	BET_PROCESSED = 1

	# Message header format
	HEADER_CODE = '!BI'
	SIZE_HEADER = calcsize(HEADER_CODE)
	Header = namedtuple('Header', 'code len')
	Payload = namedtuple('Payload', 'data')

	def __init__(self, code, payload=None):
		"""
		Constructor method for the MessageServer class.

		Parameters:
			code (int): The message code.
			payload (list or None): The payload of the message. Default is None.
		"""
		if payload is None:
			payload = []
		payload_bytes = self._pack_payload(payload)

		self.header = self.Header(code, len(payload_bytes))
		self.payload = self.Payload(payload_bytes)

	def encode(self):
		"""
		Encodes the message into a byte string.

		Returns:
			bytes: The encoded message.
		"""
		header = pack(self.HEADER_CODE, self.header.code, self.header.len)
		payload = pack(f'!{self.header.len}s', self.payload.data)

		return header+payload

	@staticmethod
	def decode_header(header):
		"""
		Decodes the message header from a byte string.

		Parameters:
			header (bytes): The message header.

		Returns:
			namedtuple: A named tuple representing the message header.
		"""
		return MessageServer.Header._make(unpack(MessageServer.HEADER_CODE, header))

	@staticmethod
	def decode_payload(payload_bytes):
		"""
		Decodes the message payload from a byte string.

		Parameters:
			payload_bytes (bytes): The message payload.

		Returns:
			list: The message payload as a list of strings.
		"""
		return MessageServer._unpack_payload(payload_bytes)

	def _pack_payload(self, payload):
		"""
		Packs the payload into a byte string.

		Parameters:
			payload (list): The message payload.

		Returns:
			bytes: The packed payload.
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
		return MessageServer.Payload(payload)

	@classmethod
	def bet_processed_message(cls):
		"""
		Creates a message to indicate that a bet has been processed.

		Returns:
			bytes: The encoded message.
		"""
		return cls(cls.BET_PROCESSED).encode()
