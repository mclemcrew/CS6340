import sys # Used for I/O
import os

# Assign variables to input file names
answerKeyFileName = sys.argv[1]

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Read in files and separate by sentence
with open(answerKeyFileName) as answerFile:
    answerText = answerFile.read().splitlines()

def is_not_blank(s):
    return bool(s and not s.isspace())

number = 0
textOutput = []

# Loop through each sentence and print
for sentence in answerText:
    if "TEXT" in sentence:
        number = sentence[6:]
    if not is_not_blank(sentence):
        filtered = list(filter(None,textOutput))
        my_file = os.path.join(CURRENT_FOLDER + "/data/development-anskeys/", number + '.key')
        fileObject = open(my_file,'w')
        for line in filtered:
            fileObject.write(line)
            fileObject.write("\n")
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print(filtered)
        textOutput = []

    textOutput.append(sentence)

