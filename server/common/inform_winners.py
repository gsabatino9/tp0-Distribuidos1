from multiprocessing import Process

def inform_winners(winners, consults_queue, server_flag, max_clients):
	p = Process(target = __inform_winners, args = (winners, consults_queue, server_flag, max_clients))
	p.start()
	p.join()

def __inform_winners(winners, consults_queue, server_flag, max_clients):
	agencies_ready = 0

	while agencies_ready < max_clients:
		agency = consults_queue.get()
		agency_winners = []
		for bet in winners:
			agency_winners.append(bet.document)

		agency.send_agency_winners(agency_winners)
		agency.stop()
		agencies_ready += 1

	server_flag.set()