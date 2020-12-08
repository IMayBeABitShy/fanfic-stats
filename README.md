# Fanfiction statistics

This repo provides a couple of tools to analyze fanfiction statistics. It is based on [ff2zim](https://github.com/IMayBeABitShy/ff2zim), which in turn is based on [fanficfare](https://github.com/JimmXinu/FanFicFare).

These tools expect you to already have a ff2zim project containing the fanfictions you want to analyze.

## Requirements

- python3
- all requirements in `requirements.txt` installed
- a ff2zim project containing fanfiction

## Wordclouds

Wordclouds are used to show the relative amount of occurences of words. The `make_wordcloud.py` script can be used to create one.

Simply run `python3 make_wordcloud.py /path/to/ff2zim/project wordcloud.png`.

**Additional arguments:**

- `--pairs`: instead of showing the most common words, show the most common two-word combinations
- `-i WORD`/`--ignore WORD`: exclude WORD from statistics. Can be specified any number of times.


## Chord diagrams

Chord diagrams are used to show occurences of pairings of elements. The `pairing_analyzer.py` script can be used to create a chord diagram showing statistics about pairings.

The script is rather flexible and supports showing a couple of statistics. These statistics are seperated into two categories, each with a master key and subkeys.

**Single-pairing statistics**

The `stats` masterkey holds informations about general pairing statistics, more specifical some stats about each found pairing.

The following subkeys are available:

- `occurences`: the number of occurences of this pairing, one for each story
- `follows`: the total number of followers of all stories featuring this pairing
- `favorites`: the total number of favorites of all stories featuring this pairing
- `words`: the total number of words of all stories featuring this pairing
- `chapters`: the total number of chapters of all stories featuring this pairing

**Multi-pairing statistics**

The `correlation` masterkey holds information about the correlation between pairings, e.g. which pairings commonly occur together. Currently only the `occurences` subkey is supported.

**Usage**

Simply run `python3 pairing_analyzer.py /path/to/ff2zim/project pairings.html MASTERKEY SUBKEY` to generate a **html** file containing the interactive diagrams.

*MASTERKEY* and *SUBKEY* refers to the keys mentioned above.

**Additonal options:**

- `-p`: print all gathered data
- `--adult-only`: only evaluate fanfictions marked as "mature"/"adult only"

