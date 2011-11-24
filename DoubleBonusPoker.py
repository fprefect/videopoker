#!/usr/bin/python

from functools import partial
#from videopoker import Card, Hand, HandPenalties, HandPattern, HandFilters, VideoPokerGame
from videopoker import *

class DoubleBonusPoker(VideoPokerGame):
	""" Table from http://www.videopokerballer.com/strategy/double-bonus/ """

	num_cards = 5

	patterns = (
		HandPattern("Pat Royal Flush", filters=[partial(HandFilters.straight_flush, to=14)], test=["Th","Jh","Qh","Kh","Ah"]),
		HandPattern("Four of a Kind Aces", count=4, filters=[partial(HandFilters.ofakind, ranks=(14,))], test=["Ac","Ah","Ad","As","3c"]),
		HandPattern("Four of a Kind Twos, Threes, Fours", count=4, filters=[partial(HandFilters.ofakind, ranks=(2,3,4))], test=["2h","2s","2c","2d","7c"]),
		HandPattern("Four of a Kind Fives - Kings", count=4, filters=[partial(HandFilters.ofakind, ranks=range(5,13+1))], test=["7c","7d","7h","7s","Jc"]),
		HandPattern("Pat Straight Flush", filters=[HandFilters.straight_flush], test=["6h","7h","8h","9h","Th"]),
		HandPattern("Royal Flush Draw", count=4, filters=[HandFilters.straight_flush], test=["Th","Jh","Qh","Kh","4h"]),
		HandPattern("Three of a Kind Aces", count=3, filters=[partial(HandFilters.ofakind, ranks=(14,))], test=["Ac","Ad","Ah","Js","8c"]),
		HandPattern("Pat Full House", filters=[partial(HandFilters.ofakind, count=3), partial(HandFilters.ofakind, count=2)], test=["Ac","Ad","As","Js","Jc"]),
		HandPattern("Pat Flush", filters=[HandFilters.flush], test=["Ac","Jc","6c","5c","4c"]),
		HandPattern("Three of a Kind Twos, Threes, Fours", count=3, filters=[partial(HandFilters.ofakind, ranks=(2,3,4))]), #   6.7105
		HandPattern("Three of a Kind Fives - Kings", count=3, filters=[partial(HandFilters.ofakind, ranks=range(5,13+1))]), #   5.4339
		HandPattern("Pat Straight", filters=[HandFilters.straight]), # 5.0000
		HandPattern("Open Straight Flush Draw", count=4, filters=[HandFilters.open_straight, HandFilters.flush]), # 3.7383
		HandPattern("Inside Straight Flush Draw", count=4, filters=[HandFilters.flush, HandFilters.inside_straight]), # 2.4894
		HandPattern("Two Pair", filters=[HandFilters.twopair]), # 1.7660
		HandPattern("Pair of Aces", count=2, filters=[partial(HandFilters.ofakind, ranks=(14,))]), # 1.7635
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
		HandPattern("Pair of Jacks, Queens, Kings",  count=2,
			filters=[partial(HandFilters.ofakind, ranks=(11,12,13))]), # 1.4582
		HandPattern("K-Q-Ts, K-J-Ts (w/ one straight penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,12,13),(10,11,13))), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.4542
		HandPattern("A-K-Qs, A-K-Js, A-Q-Js (w/ one straight penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((12,13,14), (11,13,14), (11,12,14))), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.4450
		HandPattern("Four to a Flush, 1 High Card", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=1)]), # 1.4042
		HandPattern("K-Q-Ts, K-J-Ts (w/ two penalties)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,12,13),(10,11,13))), HandFilters.flush], 
			penalties=HandPenalties(any_count=2)), #  1.3959
		HandPattern("A-K-Ts, A-Q-Ts, A-J-Ts (w/ no penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,13,14), (10,12,14), (10,11,14))), HandFilters.flush], 
			penalties=HandPenalties(any_count=0)), #  1.3663
		HandPattern("Four to a Flush, No High Card", count=4, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=0)]), # 1.3404
		HandPattern("A-K-Ts, A-Q-Ts, A-J-Ts (w/ one straight penalty)", count=3, 
			filters=[partial(HandFilters.contains_multi, ranks_sets=((10,13,14), (10,12,14), (10,11,14))), HandFilters.flush], 
			penalties=HandPenalties(straight=1)), #  1.3395
		HandPattern("Open Four to a Straight", count=4, 
			filters=[HandFilters.open_straight]), # 0.9149
		HandPattern("Pair of Twos, Threes, Fours", count=2,
			filters=[partial(HandFilters.ofakind, ranks=(2,3,4))]), # 0.8266
		HandPattern("J-T-9 suited", count=3,
			filters=[partial(HandFilters.straight, to=11), HandFilters.flush]), #  0.7826
		HandPattern("Q-J-9 suited", count=3,
			filters=[partial(HandFilters.contains, ranks_set=(9,11,12)), HandFilters.flush]), #  0.7761
		HandPattern("Pair of Fives - Tens", count=2,
			filters=[partial(HandFilters.ofakind, ranks=range(5,10+1))]), # 0.7434
		HandPattern("Three to a Flush, One High Card", count=3, 
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=1)]), #  0.4598
		HandPattern("J-T suited (w/ three penalties)", count=2,
			filters=[partial(HandFilters.contains, ranks_set=(10,11)), HandFilters.flush],
			penalties=HandPenalties(any_count=3)), #  0.4588
		HandPattern("K-Q, K-J (w/ one Straight penalty)", count=2,
			filters=[partial(HandFilters.contains_multi, ranks_sets=((12,13),(11,13)))],
			penalties=HandPenalties(straight=1)), #  0.4574
		HandPattern("Ace (w/ no flush penalty)", count=1,
			filters=[partial(HandFilters.contains, ranks_set=(14,))],
			penalties=HandPenalties(flush=0)), #  0.4552
		HandPattern("Ace (w/ one flush penalty, no 2, 3, 4 or 5)", count=1,
			filters=[partial(HandFilters.contains, ranks_set=(14,)), partial(HandFilters.doesnt_contain, ranks_set=(2,3,4,5))],
			penalties=HandPenalties(flush=1)), #  0.4499
		HandPattern("A-K, A-Q, A-J", count=2,
			filters=[partial(HandFilters.contains_multi, ranks_sets=((13,14),(12,14),(11,14)))]), # 0.4493
		HandPattern("K-T suited", count=2,
			filters=[partial(HandFilters.contains, ranks_set=(10,13)), HandFilters.flush]), # 0.4487
		HandPattern("Ace (w/ one flush penalty)", count=1,
			filters=[partial(HandFilters.contains, ranks_set=(14,))],
			penalties=HandPenalties(flush=1)), #  0.4487
		HandPattern("Jack (w/ no flush penalty)", count=1,
			filters=[partial(HandFilters.contains, ranks_set=(11,))],
			penalties=HandPenalties(flush=0)), #  0.4451
		HandPattern("3 to a St. Flush, 2 Gaps, 0 Hi Cards (St. penalty)", count=3,
			filters=[partial(HandFilters.high_card, count=0), HandFilters.flush, partial(HandFilters.inside_straight, holes=2)],
			penalties=HandPenalties(straight=1)), #  0.4431
		HandPattern("Queen", count=1, filters=[partial(HandFilters.contains, ranks_set=(12,))]), #  0.4341
		HandPattern("King", count=1, filters=[partial(HandFilters.contains, ranks_set=(13,))]), #  0.4310
		HandPattern("Jack (w/ one flush penalty)", count=1,
			filters=[partial(HandFilters.contains, ranks_set=(11,))],
			penalties=HandPenalties(flush=1)), #  0.4306
		HandPattern("Four to an Inside Straight, no High Cards", count=4,
			filters=[HandFilters.inside_straight, partial(HandFilters.high_card, count=0)]), # 0.4255
		HandPattern("Three to a Flush, no High Cards", count=3,
			filters=[HandFilters.flush, partial(HandFilters.high_card, count=0)]), # 0.3608
		# Everything Else: Draw Five New Cards     0.3231
	)

from pprint import pprint

class PokerGameTests:
	"""
	game_class = DoubleBonusPoker
	self.tests = (
		{id: "Test1", cards:cards, result:expected result, exception}
	)
	"""

	def run(self):
		success = 0
		failed = 0
		count = 0

		game = self.game_class()

		for t in self.tests:
			print "Testing", t["id"], "...",
			count += 1
			try:
				hand = Hand(t["cards"])
				result = game.best_plays(hand)
			except Exception, e:
				if "exception" in t:
					if type(e) != t["exception"]:
						print "failed: got the wrong exception:", repr(e)
						failed += 1
						continue
				else:
					print "failed: got exception", repr(e)
					failed += 1
					continue
				
			if "result" in t and t["result"] != result:
				print "failed, should have been",
				pprint(result)
				failed += 1
				continue
			print "success"
			success += 1
		print "="*80
		print "= Results: %d / %d => %02f%% success" % (success, count, 100.0*(success*1.0/count))
		print "="*80


class DoubleBonusPokerTests(PokerGameTests):
	game_class = DoubleBonusPoker
	tests = (
		{"id":"Double Bonus wrong number of cards", "cards":[], "exception":ValueError},
		{"id":"Pat Royal Flush (sorted)", "cards":[Card(x,'c') for x in range(10,14+1)], "result":[]},
		{"id":"Pat Royal Flush (unsorted)", "cards":[Card(x,'c') for x in range(10,14+1)], "result":[]},
	)

if __name__ == "__main__":

	DoubleBonusPokerTests().run()

