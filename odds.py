from videopoker import Card, Hand

from itertools import combinations
from collections import defaultdict
from operator import itemgetter

def combin(n, k):
	if not (0 <= k <= n):
		return 0
	p = 1.0
	for t in xrange(min(k, n - k)):
		p = (p * (n - t)) // (t + 1)
	return p


class FiveCardPokerOdds:
	deck_len = 52
	hand_len = 5

	def _num_suits(self, cards):
		return len(set([c.suit for c in cards]))

	def _all_suited(self, cards, min_len):
		return [h for size in xrange(len(cards), min_len-1, -1) for h in combinations(cards, size) if self._num_suits(h) == 1]

	def _longest_rank_list(self, cards):
		ranks = defaultdict(list)
		for c in cards:
			ranks[c.rank].append(c)
		assert len(ranks) > 0
		longest_rank_len = max([len(ranks[r]) for r in ranks])
		rl = []
		for r in ranks:
			if len(ranks[r]) == longest_rank_len:
				rl.append(ranks[r])
		return rl

	# Find the longest flush combination
	def _longest_flush(self, cards, min_length):
		for size in xrange(len(cards), min_length-1, -1):
			for subhand in combinations(cards, size):
				if self._num_suits(subhand) == 1:
					return Hand(subhand)
		return None

	def _subhand_straight_odds(self, hand, flush=False):
		ranks = [c.rank for c in hand]

		if ranks[-1] - ranks[0] > 4:
			return 0

		missing = []
		low = max(1, ranks[-1] - 4)
		for i in range(low, low+5):
			if i > ranks[0] or i + 5 - 1 > 14:
				break
			missing.append(set(range(i, i+5)) - set(ranks))
		
		discard_len = 5 - len(hand)

		if flush:
			suits = 1
		else:
			suits = 4

		for x in missing:
			assert len(x) >= discard_len

		return sum([combin(suits * len(x), discard_len) for x in missing]) / combin(47, discard_len) 

	## =====
	
	def royal_flush(self, cards):
		# keep only royal cards
		reduced = [c for c in cards if c.rank in range(10, 14+1)]

		if len(reduced) == 0:
			return ([], 0.0)

		hand = self._longest_flush(reduced, min_length=1)

		if not hand:
			return ([], 0.0)

		if len(hand) == 5:
			return (cards, 1.0)

		discard_len = self.hand_len - len(hand)

		return (hand, 1.0 / combin(self.deck_len - self.hand_len, discard_len))


	def straight_flush(self, cards, min_len=3):
		best_hand = ([], 0.0)
		for h in self._all_suited(cards, min_len):
			odds = self._subhand_straight_odds(h, flush=True)

			if best_hand[1] < odds:
				best_hand = (h, odds)

		return best_hand
	
	def four_aces(self, cards):
		aces = [c for c in cards if c.rank == 14]
		aces_remaining = 4 - len(aces)
		if aces_remaining == 0:
			return (cards, 1.0)
		discard_len = self.hand_len - len(aces)
		return (aces, 1.0 / combin(47, discard_len))

	def four_of_a_kind(self, cards):
		keeps = self._longest_rank_list(cards)
		assert len(keeps) > 0
		discard_len = self.hand_len - len(keeps[0])
		# num_sets * combin(num_in_useful_sets, cards_needed) / combin(cards_left_in_deck, discard_len)
		return (keeps, 1.0 / combin(47, discard_len))

	def full_house(self, cards):
		keeps = self._longest_rank_list(cards)
		assert len(keeps) > 0

		discard_len = self.hand_len - len(keeps[0])

		# num_sets * combin(num_in_useful_sets, cards_needed) / combin(cards_left_in_deck, discard_len)

		if discard_len == 2:
			if len(set([c.rank for c in cards]) - set([c.rank for c in keeps[0]])) == 1:
				return (cards, 1.0) # Pat full house
			# We have trips, tossing 2 singletons
			discarded_singletons = 2 
			return (keeps, ((discarded_singletons * combin(3,2)) + (13 - 1 - discarded_singletons) * combin(4, 2)) / combin(47, 2))
		if discard_len == 3:
			# we have only a pair. Throwing away 3 singletons, or a pair and 1 singleton
			discarded_singletons = 4 - len(keeps)
			discarded_pairs = 2 - len(keeps)
			return (keeps, (discarded_singletons + (14 - 1 - discarded_singletons - discarded_pairs) * combin(4, 3)) / combin(47, 3))
		if discard_len == 4:
			return (keeps, ((combin(3,2) + 4 + 8 * combin(4,3))  + (4 * combin(3,2) + 8 * combin(4,2))) / combin(47,4))

	def straight(self, cards):
		best_hand = ([], 0.0)
		for size in xrange(4, 1, -1):
			for h in combinations(cards, size):
				odds = self._subhand_straight_odds(h)
				if best_hand[1] < odds:
					best_hand = (h, odds)

		return best_hand

	def flush(self, cards):
		keeps = self._longest_flush(cards, 2)
		discard_len = 5 - len(keeps)
		return (keeps, combin(14 - len(cards), discard_len) / combin(47, discard_len))

	def three_of_a_kind(self, cards):
		return ([], 0.0)
	
	def two_pair(self, cards):
		return ([], 0.0)

	def high_pair(self, cards):
		return ([], 0.0)


class JacksOrBetter:
	pays = (
		{"name": "Royal Flush", "test": "royal_flush", "pay": 4000},
		{"name": "Straight Flush", "test": "straight_flush", "pay": 250},
		{"name": "Four of a Kind", "test": "four_of_a_kind", "pay": 125},
		{"name": "Full House", "test": "full_house", "pay": 45},
		{"name": "Flush", "test": "flush", "pay": 30},
		{"name": "Straight", "test": "straight", "pay": 20},
		{"name": "Three of a Kind", "test": "three_of_a_kind", "pay": 15},
		{"name": "Two Pair", "test": "two_pair", "pay": 10},
		{"name": "Jacks or Better", "test": "high_pair", "pay": 5},
	)

	def best_play(self, hand):
		calc = FiveCardPokerOdds()
		plays = []
		for line in self.pays:
			keep, odds = getattr(calc, line["test"])(hand)
			expected_pay = odds * line["pay"]
			plays.append((expected_pay, line["name"], keep, odds))

		return sorted(plays, key=itemgetter(0), reverse=True)

if __name__ == "__main__":

	from pprint import pprint
	from time import time

	def test_hand(fn, hand):
		print "%s([%s]):" %  (fn.__name__, hand)
		pprint(fn(hand)) 

	odds = FiveCardPokerOdds()

	print "="*80
	test_hand(odds.royal_flush, Hand(cards_raw=["Ah","Kh","Qh","Jh","2c"]))
	test_hand(odds.royal_flush, Hand(cards_raw=["Ac","Kh","Qh","Jh","2c"]))

	print "="*80
	test_hand(odds.straight_flush, Hand(cards_raw=["Ac","Kh","Qh","Jh","2c"]))
	test_hand(odds.straight_flush, Hand(cards_raw=["Ah","Kh","Qh","Jh","2c"]))

	print "="*80
	test_hand(odds.four_aces, Hand(cards_raw=["Ah","Ac","Ad","Jh","2c"]))

	print "="*80
	test_hand(odds.four_of_a_kind, Hand(cards_raw=["Ah","Ac","Jd","Jh","2c"]))

	print "="*80
	test_hand(odds.full_house, 
		Hand(cards_raw=["Ah","Jc","Jd","Jh","2c"]))
	test_hand(odds.full_house, 
		Hand(cards_raw=["Ah","Ac","Jd","Jh","2c"]))
	test_hand(odds.full_house, 
		Hand(cards_raw=["Ah","Kc","Jd","Jh","2c"]))
	test_hand(odds.full_house, 
		Hand(cards_raw=["Ah","Kc","Jd","6h","2c"]))

	print "=" * 80
	test_hand(odds.straight, 
		Hand(cards_string="Ah,Qc,10d,9c,4c"))
	test_hand(odds.straight, 
		Hand(cards_string="Ah,Jc,10d,9c,4c"))
	test_hand(odds.straight, 
		Hand(cards_string="Kh,Qc,10d,9c,4c"))

	

	def print_best_plays(h):
		print "=" * 80

		job = JacksOrBetter()

		st = time()
		results = job.best_play(h)
		delay = time() - st

		print "Results for hand", h
		for pay, name, keeps, odds in results:
			#print odds, name, keeps
			if len(keeps) > 0:
				if not isinstance(keeps[0], Card):
					keeps = " or ".join([str(Hand(h)) for h in keeps])
				else:
					keeps = str(Hand(keeps))
			print "%.08f %s (%.8f), %s" % (pay, name, odds, keeps)
		print "## Results in %fs" % (delay)

	h = Hand(cards_string="Ah,Qc,10d,9c,4c")
	print_best_plays(h)
	h = Hand(cards_string="Ah,Qh,10h,Jh,4c")
	print_best_plays(h)

