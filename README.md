Video Poker
===========

This is just the beginnings of a video poker odds calculator. Nothing works
correctly at this point.

[videopoker.py][] / [DoubleBonusPoker.py][] uses the stats table from
[videoballer.com][]. videopoker.py is runnable, it tests the [json
data table][/data].

Most new work is in [odds.py][]. You can run it and get some debugging output. 

[filters.py][] is a collection of boolean tests against a Hand.

[table-to-json.pl][] is just a helper script for formatting
data from [videoballer.com][].


[videoballer.com]:	http://www.videopokerballer.com/strategy/double-bonus/
[filters.py]:		https://github.com/fprefect/videopoker/tree/master/filters.py
[videopoker.py]:	https://github.com/fprefect/videopoker/tree/master/videopoker.py
[DoubleBonusPoker.py]:	https://github.com/fprefect/videopoker/tree/master/DoubleBonusPoker.py
[/data]:		https://github.com/fprefect/videopoker/tree/master/data/
[table-to-json.pl]:	https://github.com/fprefect/videopoker/tree/master/table-to-json.pl
