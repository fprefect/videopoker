#!/usr/bin/perl -w

use strict;

while(<>) {
	chomp;
	my @p = split /\t/;
	next if @p != 3;

	$p[0] =~ s/\s+$//;
	my $cards = '"' . join('","', split( /-/, $p[2])) . '"';
	
	printf '{"id":"%s", "odds": %f, "example": [%s]},', $p[0], $p[1], $cards;
	print "\n";
}

