from common.utils import Bet, store_bets, load_bets, has_won
import logging

class LotteryMaker:
	def __init__(self, expected_agencies, winners_queue):
		self.expected_agencies = expected_agencies
		self.winners_queue = winners_queue

	def make_lottery(self):
		winners = []
		bets = list(load_bets())
		for bet in bets:
			if has_won(bet): winners.append(bet)

		logging.info(f'action: sorteo | result: success')

		self.winners_queue.put(winners)