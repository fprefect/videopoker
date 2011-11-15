#!/usr/bin/python

from itertools import combinations
from functools import partial
from collections import defaultdict

class Card:
	""" A standard playing card. Ranks are range 2 - 14 and suits are in c, d, h, s """

	CLUB = "c"
	DIAMOND = "d"
	HEART = "h"
	SPADE = "s"

	def __init__(self, rank, suit):
		self.rank = rank
		self.suit = suit

	def __str__(self):
		return "%d%s" % (self.rank, self.suit)

	def __repr__(self):
		return "Card(rank=%d, suit='%s')" % (self.rank, self.suit)

	def __key(self):
		return (self.rank, self.suit)

	def __hash__(self):
		return hash(self.__key())

	def __lt__(self, other):
		if self.rank == other.rank:
			return self.suit < other.suit
		return self.rank < other.rank

	def __le__(self, other):
		return self == other or self < other

	def __eq__(self, other):
		return self.__key() == other.__key()

	def __ne__(self, other):
		return not self == other

	def __gt__(self, other):
		return self != other and not self < other

	def __ge__(self, other):
		return self == other or self > other


class Hand:
	""" A collection of Cards """

	def __init__(self, cards):
		self.cards = sorted(cards)

	def __str__(self):
		return ', '.join([str(c) for c in self.cards])
	
	def __repr__(self):
		return "Hand(%s)" % (self.cards)

	def __len__(self):
		return len(self.cards)

	def __getitem__(self, key):
		return self.cards[key]

	def __iter__(self):
		return self.cards.__iter__()

	def __contains__(self, card):
		return card in self.cards

	def combinations(self, size):
		return combinations(self.cards, size)

	def diff(self, cards):
		return sorted(set(self.cards) - set(cards))


class HandPenalties:
	""" Pentalities that get calculated per subhand, used in a HandPattern """

	def __init__(self, straight=None, flush=None, high_pair=None, any_count=None):
		self.straight = straight
		self.flush = flush
		self.high_pair = high_pair
		self.any_count = any_count

	def straight_penalties(self, subhand, remaing):
		""" Straight (St.) penalty cards mean cards that interfere w/ a hand's possibility
			of making a straight. """
		return 0

	def flush_penalties(self, cards, discard):
		""" Flush penalty cards mean cards that interfere w/ a hand's possibility of making a flush. """
		if self.flush == None and self.any_count == None:
			return 0

		if not HandFilters.flush(cards):
			return 0

		suit = subhand[0].suit
		return len([1 for c in discard if c.suit == suit])

	def high_pair_penalties(self, cards, discard):
		""" High Pair (HP) penalty cards mean cards that interfere w/ a hand's possibility 
			of making a high pair (a pair Jacks or better) """
		if self.high_pair == None and self.any_count == None:
			return 0
		return HandFilters.high_card_count(discard)
		
	def match(self, hand, subhand):
		discard = hand.diff(subhand)

		st = self.straight_penalties(subhand, discard)
		fl = self.flush_penalties(subhand, discard)
		hp = self.high_pair_penalties(subhand, discard)

		if self.any_count != None and self.any_count != (st + fl + hp):
			return False

		if self.straight != None and st != self.straight:
			return False
		if self.flush != None and fl != self.flush:
			return False
		if self.high_pair != None and hp != self.high_pair:
			return False

		return True


class HandFilters:
	""" Convenience filters for HandPattern """

	@staticmethod
	def rank_counts(cards):
		d = defaultdict(lambda: 0)
		for c in cards:
			d[c.rank] += 1
		return d

	@staticmethod
	def flush(cards):
		suit = cards[0].suit
		for c in cards:
			if c.suit != suit:
				return False
		return True

	@staticmethod
	def straight(cards, to=None):
		prev = cards[0].rank
		for i in range(1, len(cards) - 1):
			if cards[i].rank != prev + 1:
				return False
			prev = cards[i].rank
		if to:
			return to == cards[len(cards) - 1].rank
		return True

	@staticmethod
	def straight_flush(cards, to=None):
		return HandFilters.straight(cards, to=to) and HandFilters.flush(cards)

	@staticmethod
	def open_straight(cards):
		if not HandFilters.straight(cards):
			return False
		if 14 in (cards[0].rank, cards[len(cards) - 1].rank):
			return False
		return True

	@staticmethod
	def inside_straight(cards):
		holes = 0
		prevrank = cards[0].rank
		for i in range(1, len(cards) - 1):
			holes += cards[i].rank - prevrank - 1
			prevrank = cards[i].rank
		return holes <= 1

	@staticmethod
	def ofakind(cards, count=2, ranks=None):
		""" returns true if cards match <count> of a kind and the matched is in ranks """
		rank_counts = HandFilters.rank_counts(cards)
		# Quickly check if we have no pairs
		if len(rank_counts) == len(cards):
			return False

		if ranks:
			return 0 < len(filter(lambda x: x == count, [rank_counts(r) for r in rank_counts if r in ranks]))
		else:
			return 0 < len(filter(lambda x: x == count, rank_counts.values()))

	@staticmethod
	def twopair(cards):
		ranks = HandFilters.rank_counts(cards)
		# Quickly check if we have no pairs
		if len(ranks) > len(cards) - 2:
			return False

		found = 0
		for r in ranks:
			if ranks[r] == 2:
				found += 1

		return found == 2

	@staticmethod
	def high_card_count(cards):
		return len([c for c in cards if c.rank > 10])

	@staticmethod
	def high_card(cards, count=1):
		return HandFilters.high_card_count(cards) == count

	@staticmethod
	def contains(cards, ranks_set):
		return 0 < len(set(ranks_set) & set([c.rank for c in cards]))

	@staticmethod
	def contains_multi(cards, ranks_sets):
		return 0 < len(filter(lambda rs: HandFilters.contains(cards, rs), ranks_sets))

class HandPattern:
	""" A pattern definition to be applied to a Hand """

	def __init__(self, id, count=None, filters=None, penalties=None, debug=False):
		self.id = id
		self.filters = filters
		self.count = count
		self.penalties = penalties
		self.debug = debug

	def combination_size(self, hand):
		if not self.count:
			return len(hand)
			
		if self.count > 0:
			return self.count

		if self.count < 0:
			# 7 cards, count = -1, return 6
			return len(hand) + self.count
		
	def matches(self, hand):
		size = self.combination_size(hand)

		subhands = hand.combinations(size)

		for fn in self.filters:
			if self.debug:
				print "Applying filter", fn.__name__
			subhands = filter(fn, subhands)
			if self.debug:
				print "New Subhands:"
				print subhands

		if self.penalties:
			subhands = filter(partial(self.penalties.match, hand), subhands)

		return subhands

		
class PokerGame:
	""" Definition of the video poker game up for evaluation """

	num_cards = 5

	paytable = {}

	patterns = (
		HandPattern("Pat Royal Flush", filters=[partial(HandFilters.straight_flush, to=14)]),
		HandPattern("Four of a Kind Aces", filters=[partial(HandFilters.ofakind, count=4, ranks=(14,))]),
		HandPattern("Four of a Kind Twos, Threes, Fours", filters=[partial(HandFilters.ofakind, count=4, ranks=(2,3,4))]),
		HandPattern("Four of a Kind Fives - Kings", filters=[partial(HandFilters.ofakind, count=4, ranks=range(5,13))]),
		HandPattern("Pat Straight Flush", filters=[HandFilters.straight_flush]),
		HandPattern("Royal Flush Draw", count=4, filters=[HandFilters.straight_flush]),
		HandPattern("Three of a Kind Aces", filters=[partial(HandFilters.ofakind, count=3, ranks=(14,))]),
		HandPattern("Pat Full House", filters=[partial(HandFilters.ofakind, count=3), partial(HandFilters.ofakind, count=2)]),
		HandPattern("Pat Flush", filters=[HandFilters.flush]),
		HandPattern("Three of a Kind Twos, Threes, Fours", filters=[partial(HandFilters.ofakind, count=3, ranks=(2,3,4))]), #   6.7105
		HandPattern("Three of a Kind Fives - Kings", filters=[partial(HandFilters.ofakind, count=3, ranks=range(5,13))]), #   5.4339
		HandPattern("Pat Straight", filters=[HandFilters.straight]), # 5.0000
		HandPattern("Open Straight Flush Draw", count=4, filters=[HandFilters.open_straight, HandFilters.flush]), # 3.7383
		HandPattern("Inside Straight Flush Draw", count=4, filters=[HandFilters.flush, HandFilters.inside_straight]), # 2.4894
		HandPattern("Two Pair", filters=[HandFilters.twopair]), # 1.7660
		HandPattern("Pair of Aces", filters=[partial(HandFilters.ofakind, count=2, ranks=(14,))]), # 1.7635
		HandPattern("Q-J-T suited (w/ no penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=12), HandFilters.flush], 
			penalties=HandPenalties(any_count=0)), #   1.5846
		HandPattern("K-Q-J suited (w/ no penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=13), HandFilters.flush], 
			penalties=HandPenalties(any_count=0)), #   1.5754
		HandPattern("Q-J-T suited (w/ one Straight penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=12), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.5634
		HandPattern("Q-J-T suited (w/ one High Pair penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=12), HandFilters.flush], 
			penalties=HandPenalties(high_pair=1)), #  1.5430
		HandPattern("K-Q-J suited (w/ one Straight penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=13), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.5384
		HandPattern("K-Q-J suited (w/ one High Pair penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=13), HandFilters.flush], 
			penalties=HandPenalties(high_pair=1)), #  1.5365
		HandPattern("Four to a Flush, 3 High Cards (w/ no penalty)", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=3)], 
			penalties=HandPenalties(any_count=0)), #    1.5319
		HandPattern("Q-J-T suited (w/ one Flush penalty)", count=3, 
			filters=[partial(HandFilters.straight, to=12), HandFilters.flush], 
			penalties=HandPenalties(flush=1)), #  1.5264
		HandPattern("Four to a Flush, 3 High Cards (w/ 1 HP penalty)", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=3)], 
			penalties=HandPenalties(high_pair=1)), #    1.5106
		HandPattern("Q-J-T suited (w/ any two penalties)", count=3, 
			filters=[partial(HandFilters.straight, to=12), HandFilters.flush], 
			penalties=HandPenalties(any_count=2)), #  1.4894
		HandPattern("K-Q-J suited (w/ any two penalties)", count=3, 
			filters=[partial(HandFilters.straight, to=13), HandFilters.flush], 
			penalties=HandPenalties(any_count=2)), #  1.4783
		HandPattern("K-Q-T suited, K-J-T suited (w/ no penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,12,13),(10,11,13))), HandFilters.flush], 
			penalties=HandPenalties(any_count=0)), #  1.4755
		HandPattern("Four to a Flush, 2 High Cards (w/ no penalty)", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=2)], 
			penalties=HandPenalties(any_count=0)), #    1.4681
		HandPattern("A-K-Qs, A-K-Js, A-Q-Js (w/ no penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((12,13,14), (11,13,14), (11,12,14))), HandFilters.flush], 
			penalties=HandPenalties(any_count=0)), #  1.4662
		HandPattern("Pair of Jacks, Queens, Kings",  
			filters=[partial(HandFilters.ofakind, count=2, ranks=(11,12,13))]), # 1.4582
		HandPattern("K-Q-Ts, K-J-Ts (w/ one straight penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,12,13),(10,11,13))), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.4542
		HandPattern("A-K-Qs, A-K-Js, A-Q-Js (w/ one straight penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((12,13,14), (11,13,14), (11,12,14))), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.4450
		HandPattern("Four to a Flush, 1 High Card", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=1)]), # 1.4042

		# K-Q-T suited, K-J-T suited (w/ two penalties*)    1.3959
		# A-K-Ts, A-Q-Ts, A-J-Ts(w/ no penalty*)    1.3663
		# Four to a flush, No High Cards    1.3404
		# A-K-Ts, A-Q-Ts, A-J-Ts (w/ one St. penalty*)  1.3395
		# Open Four to a Straight   0.9149
		# Pair of Twos, Threes, Fours   0.8266
		# J-T-9 suited  0.7826
		# Q-J-9 suited  0.7761
		# Pair of Fives through Tens    0.7434
		# Three to a Flush, One High Card   0.4598
		# J-T suited (w/ three penalties*)  0.4588
		# K-Q, K-J (w/ one Straight penalty*)   0.4574
		# Ace (w/ no flush penalty*)    0.4552
		# Ace (w/ one flush penalty + no 2, 3, 4 or 5)  0.4499
		# A-K, A-Q, A-J     0.4493
		# K-T suited    0.4487
		# Ace (w/ one flush penalty*)   0.4487
		# Jack (w/ no flush penalty*)   0.4451
		# 3 to a St. Flush, 2 Gaps, 0 Hi Cards (St. penalty*)   0.4431
		# Queen     0.4341
		# King  0.4310
		# Jack (w/ one Flush penalty*)  0.4306
		# Four to a Straight, Inside, no High Cards     0.4255
		# Three to a Flush, no High Cards   0.3608
		# Everything Else: Draw Five New Cards     0.3231
	)

	def __init__(self):
		pass

	
	def best_plays(self, hand):
		if len(hand) != self.num_cards:
			raise ValueError("Game requires %d cards, %d received" % (self.num_cards, len(hand)))

		play_list = []
		for p in self.patterns:
			print "Testing", p.id
			m = p.matches(hand)
			if len(m) > 0:
				play_list.append((p, m))
		return play_list
		
if __name__ == "__main__":
	from pprint import pprint

	h1 = Hand([
		Card(5, Card.SPADE),
		Card(6, Card.SPADE),
		Card(7, Card.CLUB),
		Card(8, Card.SPADE),
		Card(9, Card.SPADE)
	])

	h2 = Hand([Card(5, Card.HEART), Card(6, Card.HEART)])

	print "Hand 1:", h1
	print "Hand 2:", h2
	print "Hand diff:", Hand(h1.diff(h2))

	print "Hand Combinations of 3 cards in h1:"
	print "\n".join([str(Hand(cards)) for cards in h1.combinations(3)])

	game = PokerGame()
	print "Best Plays:"
	for(p, m) in game.best_plays(h1):
		print "Matched", p.id
		pprint(m)
