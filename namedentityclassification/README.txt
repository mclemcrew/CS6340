Programming Project 3 NLP Fall 2021 UofU
Michael Clemens
October 29th, 2021

Programming Language/Version: Python3

Instructions:
To run the named entity classifier, execute the following commands:
python3 feature_extraction.py official-data/big-example/train.txt official-data/big-example/test.txt

OR

More generically...
python3 feature_extraction.py [WHATEVER YOUR FILE PATH IS]/train.txt [WHATEVER YOUR FILE PATH IS]/test.txt

Tested on computer lab2-11.eng.utah.edu
OS: Red Hat Enterpirse Linux 8.4

Limitations: The location test does not work for multiple words, only a single word.
The global checks could be done in a faster way, but I optimized it a bit already.