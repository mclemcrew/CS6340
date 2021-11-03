# Programming Project NLP Fall 2021 UofU
# Information Extraction System for Domain of Corporate Acquisition Events
# Taylor Allred
# Michael Clemens

# November 10: Midpoint evaluation systems due.
# November 30: Final evaluation systems due.
# December 6, 8: Project presentations (during class).
# December 10: Final project slides and posters due

import sys # Used for I/O
import ntpath # Used for pathing
from pathlib import Path # Also used for pathing

# Assign variables to input file names (train and test)
docFile = sys.argv[1]

# Create empty list for file paths [PATH, FILENAME]
pathList = list()

# Read in files and separate by line
with open(docFile) as docList:
    docFilePath = docList.read().splitlines()

for entry in docFilePath:
    pathList.append([ntpath.dirname(entry) + "/", ntpath.basename(entry)])

print(pathList)