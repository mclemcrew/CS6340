# Programming Project 3 NLP Fall 2021 UofU
# Michael Clemens
# October 29th, 2021

import sys # Used for I/O
import ntpath # Used for pathing
from pathlib import Path # Also used for pathing
import csv # Used for CSVs

# Assign variables to input file names (train and test)
trainingFileName = sys.argv[1]
testingFileName = sys.argv[2]

# Main path for lists of files
listsFolderPath = Path("official-data/lists")

locationsFilePath = listsFolderPath / "locations.csv"
prefixesFilePath = listsFolderPath / "prefixes.txt"
prepositionsFilePath = listsFolderPath / "prepositions.txt"
suffixesFilePath = listsFolderPath / "suffixes.txt"

# Get the base names
trainingFileNameCondensed = ntpath.basename(trainingFileName)
testingFileNameCondensed = ntpath.basename(testingFileName)

trainingFileNameCondensed = trainingFileNameCondensed[:trainingFileNameCondensed.rfind(".")]
testingFileNameCondensed = testingFileNameCondensed[:testingFileNameCondensed.rfind(".")]

# The header column
fields = ['LABEL','ABBR','CAP','GLOBCAP', 'GLOBPREF', 'GLOBSUFF','LOC','POS','POS+1','POS-1','PREF','SUFF','WORD','WORD+1','WORD-1']

# Read in files and separate by line
with open(trainingFileName) as trainingFile:
    trainingText = trainingFile.read().splitlines()

with open(testingFileName) as testFile:
    testText = testFile.read().splitlines()

# Since the locations are in a csv, we have to read these in differently
locText = []

with open(locationsFilePath, 'r') as f:
    reader = csv.reader(f)
    rowNr = 0
    for row in reader:
        if rowNr >= 1:
            locText.append([row[0],row[1]])

        rowNr = rowNr + 1

with open(prefixesFilePath) as prefixFile:
    prefixText = prefixFile.read().splitlines()

with open(prepositionsFilePath) as prepositionFile:
    prepositionText = prepositionFile.read().splitlines()

with open(suffixesFilePath) as suffixFile:
    suffixText = suffixFile.read().splitlines()

# Remove carriage returns from lists, splits based on whitespace
trainingText = list(map(lambda x: x.split(),trainingText))
testText = list(map(lambda x: x.split(),testText))

# Abbreviation Test
def abbrTest(word: str):
    # If last character is a period
    period = word[-1:] == '.'
    textSplit = word.split('.')
    textSplitBoolean = True
    textContainsBoolean = True
    # Make sure it contains a period
    if "." not in word:
        textContainsBoolean = False
    phraseLength = 0
    # At least one character has to be alphabetic
    for phrase in textSplit:
        phraseLength += len(phrase)
        if not phrase.isalpha() and len(phrase) > 0:
            textSplitBoolean = False
    
    alpha = textContainsBoolean and textSplitBoolean and (phraseLength > 0)
    # Make sure length is greater than just 1 and less than 4.  
    length = len(word) <= 4 and len(word) > 1
    if period and alpha and length:
        return 1
    return 0

# Capitalization Test
def capTest(word: str):
    if word[0].isupper():
        return 1
    return 0

# Location Test
def locTest(word: str):
    locationBool = False
    # Is the word in locations.csv
    for location in locText:
        if(word.lower() == location[0].lower() or word.lower() == location[1].lower()):
            locationBool = True
    if locationBool == True:
        return 1
    return 0

# Prefix Test
def prefixTest(word: str):
    prefixBool = False
    # Is the previous word in prefix.txt 
    for prefix in prefixText:
        if word == prefix:
            prefixBool = True
    if prefixBool == True:
        return 1
    return 0

# Suffix Test
def suffixTest(word: str):
    suffixBool = False
     # Is the following word in prefix.txt 
    for suffix in suffixText:
        if word == suffix:
            suffixBool = True
    if suffixBool == True:
        return 1
    return 0

# Preposition Test
def prepositionTest(word: str):
    prepositionBool = False
     # Is the current word in prepositions.txt 
    for preposition in prepositionText:
        if word == preposition:
            prepositionBool = True
    if prepositionBool == True:
        return 1
    return 0

# Global Tests
def globalTests(word: str, listText: list):
    potentitalWordList = []
    # Loop through the entire filer of words
    for x in range(len(listText)):
        if(len(listText[x]) == 0):
            continue
        # If we see any word that matches our current word, store the current word, previous POS, previous WORD, and following WORD
        if word.lower() == listText[x][2].lower():
            if x == 0 or len(listText[x-1])==0:
                potentitalWordList.append([listText[x][2], 'PHIPOS', 'PHI', listText[x+1][2]])
            elif len(listText[x+1])==0:
                potentitalWordList.append([listText[x][2], listText[x-1][1], listText[x-1][2], 'OMEGA'])
            else: 
                potentitalWordList.append([listText[x][2], listText[x-1][1], listText[x-1][2], listText[x+1][2]])

    # Setup bools
    capNum = 0
    prefNum = 0
    suffNum = 0

    # Loop through all the potential matches
    for x in range(len(potentitalWordList)):
        alpha = potentitalWordList[x][0].isalpha()
        preposition = True if not prepositionTest(potentitalWordList[x][0].lower()) == 1 else False
        starting = True if potentitalWordList[x][1] != 'PHIPOS' else False
        cap = True if capTest(potentitalWordList[x][0]) == 1 else False
        prefix = True if prefixTest(potentitalWordList[x][2]) == 1 else False
        ending = True if potentitalWordList[x][3] != 'OMEGA' else False
        suffix = True if suffixTest(potentitalWordList[x][3]) == 1 else False
        matchingCase = True if word == potentitalWordList[x][0] else False
        # Assertions for each global case
        if alpha and preposition and starting and cap:
            capNum = 1
        if alpha and starting and matchingCase and prefix:
            prefNum = 1
        if alpha and ending and matchingCase and suffix:
            suffNum = 1
        
    return [capNum, prefNum, suffNum]

trainingCSVData = []
testingCSVData = []

# Loop through all the words in the training file
for x in range(len(trainingText)):
    # If row is blank
    if len(trainingText[x])==0:
        continue

    WORD_BEFORE = False
    WORD_BEFORE_POS = False
    WORD_AFTER = False
    WORD_AFTER_POS = False

    # If next row is blank
    if len(trainingText[x+1])==0:
        WORD_AFTER = 'OMEGA'
        WORD_AFTER_POS = 'OMEGAPOS'
    
    else:
        WORD_AFTER = WORD_AFTER if WORD_AFTER is not False else trainingText[x+1][2]
        WORD_AFTER_POS = WORD_AFTER_POS if WORD_AFTER_POS is not False else trainingText[x+1][1]

    # If we are on our first iteration or the previous word is blank
    if x == 0 or len(trainingText[x-1])==0:
        WORD_BEFORE = 'PHI'
        WORD_BEFORE_POS = 'PHIPOS'

    else:
        WORD_BEFORE = WORD_BEFORE if WORD_BEFORE is not False else trainingText[x-1][2]
        WORD_BEFORE_POS = WORD_BEFORE_POS if WORD_BEFORE_POS is not False else trainingText[x-1][1]

    LABEL = trainingText[x][0]
    WORD = trainingText[x][2]
    POS = trainingText[x][1]
    ABBR = abbrTest(WORD)
    CAP = capTest(WORD)
    LOC = locTest(WORD)
    PREF = prefixTest(WORD_BEFORE)
    SUFF = suffixTest(WORD_AFTER)

    GLOBAL = globalTests(trainingText[x][2], trainingText)
    GLOBCAP = GLOBAL[0]
    GLOBPREF = GLOBAL[1]
    GLOBSUFF = GLOBAL[2]

    trainingCSVData.append({'LABEL':LABEL,'ABBR':ABBR,'CAP':CAP,'GLOBCAP':GLOBCAP, 'GLOBPREF':GLOBPREF, 'GLOBSUFF':GLOBSUFF,'LOC':LOC,'POS':POS,'POS+1':WORD_AFTER_POS,'POS-1':WORD_BEFORE_POS,'PREF':PREF,'SUFF':SUFF,'WORD':WORD,'WORD+1':WORD_AFTER,'WORD-1':WORD_BEFORE})

# Loop through all the words in the testing file
for x in range(len(testText)):
    # If row is blank
    if len(testText[x])==0:
        continue

    WORD_BEFORE = False
    WORD_BEFORE_POS = False
    WORD_AFTER = False
    WORD_AFTER_POS = False

    # If next row is blank
    if len(testText[x+1])==0:
        WORD_AFTER = 'OMEGA'
        WORD_AFTER_POS = 'OMEGAPOS'
    
    else:
        WORD_AFTER = WORD_AFTER if WORD_AFTER is not False else testText[x+1][2]
        WORD_AFTER_POS = WORD_AFTER_POS if WORD_AFTER_POS is not False else testText[x+1][1]

    # If we are on our first iteration or the previous word is blank
    if x == 0 or len(testText[x-1])==0:
        WORD_BEFORE = 'PHI'
        WORD_BEFORE_POS = 'PHIPOS'

    else:
        WORD_BEFORE = WORD_BEFORE if WORD_BEFORE is not False else testText[x-1][2]
        WORD_BEFORE_POS = WORD_BEFORE_POS if WORD_BEFORE_POS is not False else testText[x-1][1]


    LABEL = testText[x][0]
    WORD = testText[x][2]
    POS = testText[x][1]
    ABBR = abbrTest(WORD)
    CAP = capTest(WORD)
    LOC = locTest(WORD)
    PREF = prefixTest(WORD_BEFORE)
    SUFF = suffixTest(WORD_AFTER)

    GLOBAL = globalTests(testText[x][2], testText)
    GLOBCAP = GLOBAL[0]
    GLOBPREF = GLOBAL[1]
    GLOBSUFF = GLOBAL[2]

    testingCSVData.append({'LABEL':LABEL,'ABBR':ABBR,'CAP':CAP,'GLOBCAP':GLOBCAP, 'GLOBPREF':GLOBPREF, 'GLOBSUFF':GLOBSUFF,'LOC':LOC,'POS':POS,'POS+1':WORD_AFTER_POS,'POS-1':WORD_BEFORE_POS,'PREF':PREF,'SUFF':SUFF,'WORD':WORD,'WORD+1':WORD_AFTER,'WORD-1':WORD_BEFORE})

# Store training data in CSV
with open(trainingFileNameCondensed + '_ft.csv', 'w') as csvFile:
    writer = csv.DictWriter(csvFile, fieldnames = fields)
    writer.writeheader()
    writer.writerows(trainingCSVData)

# Store testing data in CSV
with open(testingFileNameCondensed + '_ft.csv', 'w') as csvFile:
    writer = csv.DictWriter(csvFile, fieldnames = fields)
    writer.writeheader()
    writer.writerows(testingCSVData)