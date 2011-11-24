#!/usr/bin/python

from functools import partial
from collections import defaultdict
import videopoker

def to_str(fn):
	if isinstance(fn, partial):
		return "partial(%s, **kwargs=%s))" % (fn.func.__name__, fn.keywords)
	else:
		return fn.__name__

def rank_counts(cards):
	d = defaultdict(lambda: 0)
	for c in cards:
		d[c.rank] += 1
	return d

def flush(cards):
	return 1 == len(set(videopoker.Hand(cards).suits()))

def straight(cards, to=None):
	prevrank = cards[0].rank
	for i in range(1, len(cards)):
		if cards[i].rank != prevrank + 1:
			return False
		prevrank = cards[i].rank

	if to:
		return to == cards[-1].rank

	return True

def straight_flush(cards, to=None):
	return straight(cards, to=to) and flush(cards)

def open_straight(cards):
	if not straight(cards):
		return False
	if 14 in (cards[0].rank, cards[-1].rank):
		return False
	return True

def inside_straight(cards, holes=1):
	holes_found = 0
	ranks = videopoker.Hand(cards).ranks()
	prev_rank = ranks[0]
	for i in range(1, len(ranks)):
		if prev_rank == ranks[i]:
			return False
		holes_found += ranks[i] - prev_rank - 1
		prev_rank = ranks[i]
	return holes_found == holes

def ofakind(cards, count=None, ranks=None):
	""" returns true if cards match <count> of a kind and the matched is in ranks """
	if not count:
		count = len(cards)

	rc = rank_counts(cards)
	# Quickly check if we have no pairs
	if len(rc) == len(cards):
		return False

	if ranks:
		return 0 < len(filter(lambda x: x == count, [rc[r] for r in rc if r in ranks]))
	else:
		return 0 < len(filter(lambda x: x == count, rc.values()))

def pair(cards, ranks=None):
	return ofakind(cards, count=2, ranks=ranks)

def trips(cards, ranks=None):
	return ofakind(cards, count=3, ranks=ranks)

def quads(cards, ranks=None):
	return ofakind(cards, count=4, ranks=ranks)

def twopair(cards):
	ranks = rank_counts(cards)
	# Quickly check if we have no pairs
	if len(ranks) > len(cards) - 2:
		return False

	found = 0
	for r in ranks:
		if ranks[r] == 2:
			found += 1

	return found == 2

def high_card_count(cards):
	return len([c for c in cards if c.rank > 10])

def high_card(cards, count=1):
	return high_card_count(cards) == count

def contains(cards, ranks):
	return len(ranks) < len(set(ranks) & set([c.rank for c in cards]))

def contains_multi(cards, rank_sets):
	return 0 < len(filter(lambda rs: contains(cards, rs), rank_sets))

def doesnt_contain(cards, ranks):
	return 0 >= len(set(ranks) & set([c.rank for c in cards]))


if __name__ == "__main__":
	h = videopoker.Hand(cards_raw=["Ts", "Js", "Qs", "Ks", "5d"])
	print h
	for c in h.combinations(4):
		print "-"*40
		print c
		print doesnt_contain(c, [2,3,4,5,6,7,8,9])
		
