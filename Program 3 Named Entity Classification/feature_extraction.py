# Programming Project 3 NLP Fall 2021 UofU
# Michael Clemens
# October 29th, 2021

import sys # Used for I/O
import math # Used for rounding and log2
import random # Used for random generation of choices for sentences

# Assign variables to input file names
trainingFileName = sys.argv[1]
typeName = sys.argv[2].replace('-','')
testFileName = sys.argv[3]

# Read in files and separate by sentence
with open(trainingFileName) as trainingFile:
    trainingText = trainingFile.read().splitlines()

with open(testFileName) as testFile:
    testText = testFile.read().splitlines()

# Remove carriage returns from lists, removes sensitivity to case and splits based on whitespace
trainingText = list(map(lambda x: x.lower().split(),trainingText))
testTextUnaltered = list(map(lambda x: x.split(),testText))
testText = list(map(lambda x: x.lower().split(),testText))

# Create a dictionary for probability distribution of UniGram and BiGram words
unigramTraining = dict()
bigramTraining = dict()

# Train unigram model
for sentence in trainingText:
    # For each word...
    for word in sentence:
        # Add one to the frequency if we find it, otherwise just add it to the dictionary
        if word in unigramTraining:
            unigramTraining[word] += 1
        else:
            unigramTraining[word] = 1

# Train bigram model
for sentence in trainingText:
    # Add phi to the start of a sentence
    sentence = ['phi'] + sentence
    # For the length of the sentence
    for x in range(len(sentence)-1):
        # Create the bigram
        key = tuple([sentence[x], sentence[x+1]])
        # Add one to the frequency if we find it, otherwise just add it to the dictionary
        if key in bigramTraining:
            bigramTraining[key] += 1
        else:
            bigramTraining[key] = 1

# If we are building a probability chart...
if typeName == 'test':
    # For each sentence we come across
    for sentence, sentenceUnaltered in zip(testText,testTextUnaltered):
        #Initialize all probabilites
        unigramProbability = 0
        bigramProbabiliy = 0
        bigramSmoothProbabiliy = 0

        print("S =", *sentenceUnaltered, "\n")

        # Unigram Probability (frequency of word/sum(frequency of all words))
        for word in sentence:
            if word in unigramTraining:
                unigramProbability += math.log2(unigramTraining[word]/sum(unigramTraining.values()))

        # Bigram Smoothed Probability ((frequency of bigram+1)/(frequency of first word in bigram+num of unique words)
        sentence = ['phi'] + sentence
        for y in range(len(sentence)-1):
            key = tuple([sentence[y], sentence[y+1]])
            # If the bigram exists
            if key in bigramTraining:
                # Handle phi separately (count one for each sentence provided)
                if sentence[y] == 'phi':
                    bigramSmoothProbabiliy += math.log2((bigramTraining[key]+1)/(len(trainingText)+len(unigramTraining)))
                else:
                    bigramSmoothProbabiliy += math.log2((bigramTraining[key]+1)/(unigramTraining[sentence[y]]+len(unigramTraining)))
            # Otherwise, just have one in the num
            else:
                # Handle phi separately (count one for each sentence provided)
                if sentence[y] == 'phi':
                    bigramSmoothProbabiliy += math.log2((1)/(len(trainingText)+len(unigramTraining)))
                else:
                    bigramSmoothProbabiliy += math.log2((1)/(unigramTraining[sentence[y]]+len(unigramTraining)))

        # Bigram Unsmoothed Probability (frequency of bigram/frequency of first word in bigram)
        for x in range(len(sentence)-1):
            key = tuple([sentence[x], sentence[x+1]])
            # If the bigram exists
            if key in bigramTraining:
                # Handle phi separately (count one for each sentence provided)
                if sentence[x] == 'phi':
                    bigramProbabiliy += math.log2(bigramTraining[key]/len(trainingText))
                else:
                    bigramProbabiliy += math.log2(bigramTraining[key]/unigramTraining[sentence[x]])
            # Otherwise the probability will be undefined
            else:
                bigramProbabiliy = "undefined"
                break

        # Printing scheme
        print("Unsmoothed Unigrams, logprob(S) = {}".format(format(round(unigramProbability,4),'.4f')))

        if type(bigramProbabiliy) == str:
            print("Unsmoothed Bigrams, logprob(S) = {}".format(bigramProbabiliy))
        else:
            print("Unsmoothed Bigrams, logprob(S) = {}".format(format(round(bigramProbabiliy,4),'.4f')))

        print("Smoothed Bigrams, logprob(S) = {}\n".format(format(round(bigramSmoothProbabiliy,4), '.4f')))

# If we are building a sentence generator...
elif typeName == 'gen':
    # Language Generator
    for seedWord in testTextUnaltered:
        print ("Seed = {}\n".format(seedWord[0]))
        # We need to generate 10 sentences
        for f in range(10):
            # Sentence Construction
            sentenceOutput = list()
            sentenceOutput.append(seedWord[0])
            # Start with the seed
            seed = seedWord[0].lower()

            # Maximum of 10 words..this will loop through 10 times with the way it's constructed
            for g in range(9):
                # If we encounter an end punctuation, we are done
                if seed == '.' or seed == '?' or seed == '!':
                    break

                # Initialize the dictionary and lists
                modifiedDict = dict()
                sampleList = list()
                weightList = list()

                # If the bigram exists in the bigram dict, let's create a new dict with only the relevant terms
                for (a, b), value in bigramTraining.items():
                    if(a==seed):
                        modifiedDict[(a, b)] = value

                # If the dictionary doesn't have anything after the addition, then bigram didn't exist so let's end this
                if len(modifiedDict) == 0:
                    break

                # For each bigram in our new dict..
                for (x, y), value in modifiedDict.items():
                    # Add the word that appears in the 2nd position of the bigram
                    sampleList.append(y)
                    # Add the weight associated with that bigram
                    weightList.append(value/sum(modifiedDict.values()))

                # Choose a random value based on the weights
                seed = random.choices(sampleList, weightList, k=1)[0]

                # That's now the new seed
                sentenceOutput.append(seed)

            # Since indexing starts at 0, let's add 1
            count = f + 1
            # Print the sentence
            print("Sentence {}:".format(count),*sentenceOutput)
        print()