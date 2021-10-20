# Programming Project 1 NLP Fall 2021 UofU
# Michael Clemens
# September 15th, 2021

import sys

# Assign variables to input file names
dictionaryFileName = sys.argv[1]
rulesFileName = sys.argv[2]
testFileName = sys.argv[3]

# Read in files
with open(dictionaryFileName) as dictionaryFile:
    dictionaryText = dictionaryFile.read().splitlines()

with open(rulesFileName) as rulesFile:
    rulesText = rulesFile.read().splitlines()

with open(testFileName) as testFile:
    testText = testFile.read().splitlines()

# Remove carriage returns from lists
dictionaryText = list(map(lambda x: x.split(),dictionaryText))
rulesText = list(map(lambda x: x.split(),rulesText))

# Inputs: rootWord, ruleList (up to this point)
# Outputs: potential rule list to follow, the POS changes associated with those rules
def morphological_analysis(rootWordMorph: str, ruleListMorph: list):
    potentialRuleList = list()
    potentialPOSList = list()
    for rule in rulesText:
        if rule[0] in ruleListMorph:
            continue
        if rule[1] == 'SUFFIX':
            if (rootWordMorph[len(rootWordMorph)-len(rule[2]):].lower()) == rule[2]:
                potentialRuleList.append(rule[0])
                potentialPOSList.append([rule[4],rule[6]])
        elif rule[1] == 'PREFIX':
            if (rootWord[:len(rule[2])].lower()) == rule[2]:
                potentialRuleList.append(rule[0])
                potentialPOSList.append([rule[4],rule[6]])   
    return potentialRuleList, potentialPOSList

# Inputs: baseWord, ruleList (up to this point)
# Outputs: modified root word based on the rules given
def transform_word(pathWord: str, rulePath: str):
    if rulesText[int(rulePath)-1][1] == 'SUFFIX':
        if rulesText[int(rulePath)-1][3] == '-':
            pathWord = pathWord[:len(pathWord)-len(rulesText[int(rulePath)-1][2])].lower()
        else:
            pathWord = pathWord[:len(pathWord)-len(rulesText[int(rulePath)-1][2])].lower() + rulesText[int(rulePath)-1][3]
    else:
        if rulesText[int(rulePath)-1][3] == '-':
            pathWord = pathWord[len(rulesText[int(rulePath)-1][2]):].lower()
        else:
            pathWord =  pathWord[len(rulesText[int(rulePath)-1][2]):].lower() + rulesText[int(rulePath)-1][3]
    return pathWord

# Loop through every word in the test file
for testWord in testText:
    # Used to determine if dictionary was used or not
    dictionaryBoolean = False
    # Create a temporary POS list
    tempPOSList = list()
    # Loop through every word in the dictionary
    for dictionaryWord in dictionaryText:
        # If the test word is found in the dictionary, let's see how many times it's in the dictionary
        if testWord.lower() == dictionaryWord[0]:
            tempPOSList.append(dictionaryWord)
        # If the word is the same, sort by the POS tag alphabetically 
        tempPOSList = sorted(tempPOSList, key=lambda x : x[1])

    # For every potential POS, let's list them here
    for entry in tempPOSList:
        if len(entry) > 2:
            print("WORD={}  POS={}  ROOT={} SOURCE={}   PATH={}".format(testWord,entry[1],entry[3],'dictionary','-'))
        else:
            print("WORD={}  POS={}  ROOT={} SOURCE={}   PATH={}".format(testWord,entry[1],entry[0],'dictionary','-'))
        dictionaryBoolean = True

    # If the word wasn't found in the dictionary, attempt morphological analysis
    if dictionaryBoolean == False:
        # Save the testWord we are working with
        rootWord = testWord
        # Initialize the rule, POS, and word list
        ruleList = list()
        posList = list()
        wordList = list()
        # Used to determine if a rule was used or not
        ruleBoolean = False
        # Initialize the rule set and POS set
        initialList, initialPOSList = morphological_analysis(rootWord,list())

        # For each viable rule, loop through the list and see if the derived word matches a word in the dictionary
        for path, pos in zip(initialList, initialPOSList):
            # Save the new word
            pathWord = rootWord
            ruleBoolean = True
            pathWord = transform_word(pathWord, path)

            # If that word is in the dictionary, we've reached the end
            if any(pathWord in x for x in dictionaryText):
                ruleList.append(path)
                posList.append(pos)
                wordList.append(pathWord)

            # If the word isn't found in the dictionary, let's see if there are other paths to take
            if not any(pathWord in x for x in dictionaryText):
                # Round two
                secondList, secondPOSList = morphological_analysis(pathWord, rulesText[int(path)-1][0])

                for secondPath, secondPOS in zip(secondList,secondPOSList):
                    secondWord = pathWord
                    secondWord = transform_word(secondWord, secondPath)

                    if any(secondWord in x for x in dictionaryText):
                        ruleList.append([path,secondPath])
                        posList.append([pos,secondPOS])
                        wordList.append(secondWord)

                    # If the word isn't found in the dictionary, let's see if there are other paths to take
                    if not any(secondWord in x for x in dictionaryText):
                        thirdList, thirdPOSList = morphological_analysis(secondWord, [rulesText[int(path)-1][0],rulesText[int(secondPath)-1][0]])

                        # Round three and this is wrong but it's too late and I'm sorry to whoever reads this
                        for thirdPath, thirdPOS in zip(thirdList,thirdPOSList):
                            thirdWord = secondWord
                            thirdWord = transform_word(thirdWord, thirdPath)

                            if any(thirdWord in x for x in dictionaryText):
                                ruleList.append([path,secondPath,thirdPath])
                                posList.append([pos,secondPOS,thirdPOS])
                                wordList.append(thirdWord)
                            if not any(secondWord in x for x in dictionaryText):
                                continue

        # Validation to ensure the POS matches
        validationList = list()

        # Loops through each of the possible paths and makes sure that the POS traversal matches
        # If it matches, validationBoolean = 'True' otherwise = 'False'
        for singleRuleList, singlePOSList, singleWord in zip(ruleList,posList,wordList):
            index_row = [dictionaryText.index(row) for row in dictionaryText if singleWord in row]
            possiblePOSList = list()
            for index in index_row:
                possiblePOSList.append(dictionaryText[index][1])

            tempPOS = 'default'
            validationBoolean = 'True'
            for x in range(len(singlePOSList)):
                if isinstance(singlePOSList[0], list):
                    if x == 0:
                        if singlePOSList[len(singlePOSList)-x-1][0] in possiblePOSList:
                            tempPOS = singlePOSList[len(singlePOSList)-x-1][1]
                            continue
                    
                    if singlePOSList[len(singlePOSList)-x-1][0] == tempPOS:
                        tempPOS = singlePOSList[len(singlePOSList)-x-1][1]
                        continue
                    else:
                        validationBoolean = 'False'
                        validationList.append(validationBoolean)
                        break
                else:
                    if singlePOSList[0] in possiblePOSList:
                        break
                    else:
                        validationBoolean = 'False'
                        validationList.append(validationBoolean)
                        break
            if validationBoolean == 'True':
                validationList.append(validationBoolean)
        
        # Find all of the possible paths that passed validation
        validationIndex = [i for i, x in enumerate(validationList) if x == "True"]

        # Loop through the possible viable paths and output in the correct format
        if len(validationIndex) > 0:
            for indexValue in validationIndex:
                tempList = list(ruleList[indexValue])
                ruleInt = int(tempList[0])
                tempList.reverse()
                stringPath = str(tempList).strip('[]').replace("'","").replace(" ","")
                print("WORD={}  POS={}  ROOT={} SOURCE={}   PATH={}".format(rootWord, rulesText[ruleInt-1][6], wordList[indexValue],'morphology',stringPath))
            print()
        else:
            print("WORD={}  POS={}  ROOT={} SOURCE={}   PATH={}\n".format(testWord,'noun',testWord.lower(),'default','-'))
    
    else:
        print()