#!/usr/bin/python

from itertools import combinations
from functools import partial
import simplejson as json
import filters as HandFilters

class Card:
	""" A standard playing card. Ranks are range 2 - 14 and suits are in c, d, h, s """

	CLUB = "c"
	DIAMOND = "d"
	HEART = "h"
	SPADE = "s"

	letter_rank_num = { "A": 14, "K":13, "Q":12, "J":11, "T":10 }
	#num_rank_letter = { 14: "A", 13: "K", 12: "Q", 11: "J", 10:"T" }

	def __init__(self, rank, suit):
		if rank < 2 or rank > 14:
			raise ValueError("Unknown rank")
		self.rank = int(rank)

		if suit not in (self.CLUB, self.DIAMOND, self.HEART, self.SPADE):
			raise ValueError("Unknown suit")
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
	def __init__(self, cards=None, cards_raw=None):
		if cards and cards_raw:
			raise ValueError("Cannot set Hand with both cards and cards_raw")

		if(cards_raw):
			cards = []
			for s in cards_raw:
				r = s[0:-1]
				if r in Card.letter_rank_num:
					r = Card.letter_rank_num[r]
				cards.append(Card(rank=int(r), suit=s[-1]))

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

	def ranks(self):
		return [c.rank for c in self.cards]

	def suits(self):
		return [c.suit for c in self.cards]

	def high_cards(self):
		return [c for c in self.cards if c.rank > 10]


class HandPenalties:
	""" Pentalities that get calculated per subhand, used in a HandPattern """

	def __init__(self, straight=0, flush=0, high_pair=0, kicker=None, any_count=None, debug=False):
		self.straight = straight
		self.flush = flush
		self.high_pair = high_pair
		self.kicker = kicker
		self.any_count = any_count
		self.debug = debug

	def __repr__(self):
		return "HandPenalties(" + repr({
			"straight": self.straight,
			"flush": self.flush,
			"high_pair": self.high_pair,
			"kicker": self.kicker,
			"any_count": self.any_count	
		}) + ")"

	def straight_penalties(self, cards, discard):
		""" Straight (St.) penalty cards mean cards that interfere w/ a hand's possibility
			of making a straight. """
		if not HandFilters.straight(cards):
			return 0
		low = cards[0].rank - 1
		high = cards[-1].rank + 1
		penalties = 0
		if low >= 2 and low in Hand(discard).ranks():
			penalties += 1
		if high <= 14 and high in Hand(discard).ranks():
			penalties += 1
		return penalties

	def flush_penalties(self, cards, discard):
		""" Flush penalty cards mean cards that interfere w/ a hand's possibility of making a flush. """
		if not HandFilters.flush(cards):
			return 0

		suit = cards[0].suit
		return len([1 for c in discard if c.suit == suit])

	def high_pair_penalties(self, cards, discard):
		""" High Pair (HP) penalty cards mean cards that interfere w/ a hand's possibility 
			of making a high pair (a pair Jacks or better) """
		ranks = Hand(cards).ranks()
		penalties = 0
		for c in Hand(discard).high_cards():
			if c.rank in ranks:
				penalties += 1
		return penalties

	def kicker_penalties(self, cards, discard):
		return len([1 for r in Hand(discard).ranks() if r in self.kicker])
		
	def match(self, hand, subhand):

		st, fl, hp = 0, 0, 0

		discard = hand.diff(subhand)

		if self.kicker != None:
			kp = self.kicker_penalties(subhand, discard)
			if self.debug:
				print "Penalties: kicker:", kp
			if kp > 0:
				return False

		if self.straight != None or self.any_count != None:
			st = self.straight_penalties(subhand, discard)

		if self.flush != None or self.any_count != None:
			fl = self.flush_penalties(subhand, discard)

		if self.high_pair != None or self.any_count != None:
			hp = self.high_pair_penalties(subhand, discard)

		if self.debug:
			print "Penalties: straight: %d/%s, flush: %d/%s, high pair: %d/%s, any count: %d/%s" % (
				st, str(self.straight), fl, str(self.flush), hp, str(self.high_pair), (st+fl+hp), str(self.any_count)
			)

		if self.any_count != None:
			return self.any_count == (st + fl + hp)

		if st != self.straight:
			return False

		if fl != self.flush:
			return False

		if hp != self.high_pair:
			return False

		return True

class HandPattern:
	""" A pattern definition to be applied to a Hand """

	def __init__(self, name, count=None, filters=None, penalties=None, debug=False, test=None, pays=0.0):
		self.name = name
		self.filters = filters
		self.count = count
		self.penalties = penalties
		self.debug = debug
		self.filter_class = HandFilters

	def combination_size(self, hand):
		if not self.count:
			return len(hand)
			
		if self.count > 0:
			return self.count

		if self.count < 0:
			# 7 cards, count = -1, return 6
			return len(hand) + self.count
	
	def filter_function_from_def(self, filter_def):
		try:
			kw = filter_def.copy()
			fn_name = kw["fn"]
			del kw["fn"]
		except AttributeError:
			fn_name = filter_def
			kw = None

		if kw:
			return partial(getattr(self.filter_class, fn_name), **kw)
		else:
			return getattr(self.filter_class, fn_name)

	def matches(self, hand):
		size = self.combination_size(hand)

		subhands = hand.combinations(size)

		for filter_def in self.filters:
			if self.debug:
				print "Applying filter", filter_def
			subhands = filter(self.filter_function_from_def(filter_def), subhands)
			if self.debug:
				print "New Subhands:"
				print subhands

		if self.penalties:
			subhands = filter(partial(self.penalties.match, hand), subhands)

		return subhands

	def __repr__(self):
		filter_strings = []
		for fn in self.filters:
			filter_strings.append(HandFilters.to_str(fn))
		if self.penalties:
			penalties_string = str(self.penalties)
		else:
			penalties_string = "None"
		return 'HandPattern(name="%s", count=%s, filters=[%s], penalties=%s)' % (
			self.name, self.count, ", ".join(filter_strings), penalties_string)


class VideoPokerGame:
	""" Definition of the video poker game up for evaluation """
	name = ""
	num_cards = 0
	patterns = ()

	def __init__(self, definition_file=None):
		if definition_file:
			self.load_def(definition_file)

	def __str__(self):
		return "<%s played with %d cards, %d hand patterns>" % (self.name, self.num_cards, len(self.patterns))

	def load_def(self, filename):
		with open(filename) as f:
		    jsons = "".join([line for line in f])

		obj = json.loads(jsons)

		self.name = obj["name"]
		self.num_cards = obj["num_cards"]
		self.patterns = obj["patterns"]

		for p in self.patterns:
			if "_comment" in p:
				del p["_comment"]
			if "penalties" in p:
				penalties_def = p["penalties"]
				p["penalties"] = HandPenalties(**penalties_def)

	def best_plays(self, hand, debug=False):
		if len(hand) != self.num_cards:
			raise ValueError("Game requires %d cards, %d received" % (self.num_cards, len(hand)))

		plays = []
			
		for p in self.patterns:
			hp = HandPattern(**p)
			if debug == True or debug == hp.name:
				hp.debug = debug
				if "penalties" in p:
					p["penalties"].debug = True
			m = hp.matches(hand)
			if len(m) > 0:
				plays.append((p, m))

		return plays

	def serialize(self):
		for p in self.patterns:
			print p.serialize()

	def test(self, pattern_id=None, debug=False):
		print self

		if pattern_id:
			start = pattern_id
			end = start + 1
			debug = self.patterns[start]["name"]
		else:
			start = 0
			end = len(self.patterns)

		fails = 0.0
		count = 0
		for pattern in self.patterns[start:end]:
			if "test" not in pattern:
				continue

			print count, pattern["name"], "...",

			count += 1
			plays = self.best_plays(Hand(cards_raw=pattern["test"]), debug=debug)

			try:
				assert len(plays) > 0
				assert pattern["name"] == plays[0][0]["name"]
			except AssertionError:
				if len(plays) > 0:
					match = plays[0][0]["name"]
				else:
					match = "none"
				print 'failed for %s; matched %s' % ( pattern["test"], match)
				fails += 1
				continue
			print "pass"

		print "="*80
		print "= Failed %d/%d (%02f%%)" % (fails, count, (fails/count)*100)


if __name__ == "__main__":
	game = VideoPokerGame("data/DoubleBonusPoker-10-7.json")
	game.test(25, debug=True)

