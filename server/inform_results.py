class InformResults:
	def __init__(self, winners_queue, consults_queue, max_clients):
		self.winners_queue = winners_queue
		self.consults_queue = consults_queue
		self.max_clients = max_clients

		self.winners = None

	def run(self):
		if not self.winners_queue.is_empty():
			self.winners = self.winners_queue.is_empty()