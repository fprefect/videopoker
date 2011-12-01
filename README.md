Video Poker
===========

This is just the beginnings of a video poker odds calculator. Nothing works
correctly at this point.

videopoker.py / DoubleBonusPoker.py uses the stats table from
[videoballer.com](vb_dblbonus). videopoker.py is runnable, it tests the [json
data table](./data/).

Most new work is in odds.py. You can run it and get some debugging output. 

[filters.py](./filters.py) is a collection of boolean tests against a Hand.

[table-to-json.pl](./table-to-json.pl) is just a helper script for formatting
data from [videoballer.com](vb_dblbonus)

	[vb_dblbonus]: http://www.videopokerballer.com/strategy/double-bonus/
