# Programming Project NLP Fall 2021 UofU
# Information Extraction System for Domain of Corporate Acquisition Events
# Taylor Allred
# Michael Clemens

# November 10: Midpoint evaluation systems due.
# November 30: Final evaluation systems due.
# December 6, 8: Project presentations (during class).
# December 10: Final project slides and posters due

#~~~~~~~~~

# Random thoughts for the project

#~~~~~~~~~
# Vet these candidates through a rule-based system
# Probability matrix to choose most likely answer
# ACQLOC,  DLRAMT,  SELLER,  and  STATUS  all only have a single correct answer
# Loop these through first with the highest probability and then use these answer to help inform latter options
# DLRAMT -> phrase rather than singular amount
# Recognize numeric values
# List abbreviations for dollar (these can be given as clues to our system)
# Have a scoring system based on how many rules they pass
# From the dependency/POS tree, find generalized rules that can apply and use those to traverse to rebuild the sentence from the nodes
# Looping System (multiple entities)
# Rules Paper
# X is to Y (NOUN ADJ)
# X and Y 
# X of Y and Z (NOUN NOUN NOUN)

import sys # Used for I/O
import ntpath # Used for pathing
from pathlib import Path # Also used for pathing
import os
import re # Used for regex
import spacy # NLP Models
from spacy import displacy # Visualization Tools
from  itertools import chain

def main():
    sp = spacy.load("./models/04/model-best")

    all_stopwords = sp.Defaults.stop_words # Get all stop words
    all_stopwords.add("Reuter") # Add forms for Reuter
    all_stopwords.add("reuter")
    all_stopwords.add("REUTER")
    all_stopwords.remove("in") # This is included in some status forms
    all_stopwords.remove("for") # This is included in some status forms
    all_stopwords.remove("the") # This is included in some status forms
    all_stopwords.remove("to") # This is included in some status forms
    all_stopwords.remove("its") # This is included in some status forms
    all_stopwords.remove("a") # This is included in some status forms
    all_stopwords.remove("of") # This is included in some status forms
    all_stopwords.remove("and") # This is included in some status forms

    # Doclist of files to read in
    docFile = sys.argv[1]

    # Create empty list for file paths [PATH, FILENAME]
    pathList = list()

    # Directory paths for both docs and answer keys
    developmentDocs = '/data/development-docs'
    developmentKeys = '/data/development-anskeys'

    # Used for opening and reading all the files in the development docs
    # for filename in os.listdir(os.getcwd() + developmentDocs):
    #     with open(os.path.join(os.getcwd() + developmentDocs, filename), 'r') as fileText: # open in readonly mode
    #         developmentDocText = docFilePath = fileText.read().strip().splitlines()
    #         print(developmentDocText)

    # Read in files and separate by line
    with open(docFile) as docList:
        docFilePath = docList.read().strip().splitlines()

    # Create each path by combining directory name and file name 
    for entry in docFilePath:
        pathList.append([ntpath.dirname(entry) + "/", ntpath.basename(entry)])

    # Loop through all the files in the doclist
    for path in pathList:
        with open(path[0][1:]+path[1]) as file:
            # Remove new lines, empty spaces
            documentText = file.read().replace("\n"," ").replace("  +"," ").strip()

        # Remove stop words (TODO: may need to look at removing some stop words from the list that may be in our corpus)
        big_regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, all_stopwords)))
        documentText = big_regex.sub("", documentText)
        # Removes extra spaces that may have crept in from replacements
        documentText = re.sub(' +', ' ', documentText)

        #  TESTING -> For finding digits within the text
        # re.findall(r'[^\D]+',text)

        # Create a spacy object for the entire text given
        doc = sp(documentText)

        # TESTING -> Prints out each sentence
        # for sentence in doc.sents:
        #     print(sentence)

            # TESTING -> Used for displaying the dependency graph for each sentence
            # displacy.serve(doc, style="dep", options = {'distance': 150})
            # displacy.serve(doc, style="ent")

            # TESTING -> Other way for visualizing the entities and where they start/end in the sentence
            # ents = [(e.text, e.start_char, e.end_char, e.label_) for e in doc.ents]

        # TESTING -> Loop through each entity spacy determined

        print (f"TEXT: {path[1]}")
        entityList = []
        for ent in doc.ents:
            entityList.append([ent.text, ent.label_])
            # print(f'{ent.text:{15}} {ent.label_}')
        
        if("ACQUIRED" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'ACQUIRED':
                    print (f"ACQUIRED: \"{entity[0]}\"")
        
        elif("ACQUIRED" not in chain(*entityList)):
           print (f"ACQUIRED: ---") 
        
        if("ACQBUS" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'ACQBUS':
                    print (f"ACQBUS: \"{entity[0]}\"")
        
        elif("ACQBUS" not in chain(*entityList)):
           print (f"ACQBUS: ---") 

        if("ACQLOC" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'ACQLOC':
                    print (f"ACQLOC: \"{entity[0]}\"")
        
        elif("ACQLOC" not in chain(*entityList)):
           print (f"ACQLOC: ---")

        if("DLRAMT" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'DLRAMT':
                    print (f"DLRAMT: \"{entity[0]}\"")
        
        elif("DLRAMT" not in chain(*entityList)):
           print (f"DLRAMT: ---") 

        if("PURCHASER" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'PURCHASER':
                    print (f"PURCHASER: \"{entity[0]}\"")
        
        elif("PURCHASER" not in chain(*entityList)):
           print (f"PURCHASER: ---") 

        if("SELLER" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'SELLER':
                    print (f"SELLER: \"{entity[0]}\"")
        
        elif("SELLER" not in chain(*entityList)):
           print (f"SELLER: ---") 

        if("STATUS" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'STATUS':
                    print (f"STATUS: \"{entity[0]}\"")
        
        elif("STATUS" not in chain(*entityList)):
           print (f"STATUS: ---") 

        print()
        

        # TESTING -> displays the text, POS, dependency, and head for each token (each word)
        # for token in doc:
        #     print(f'{token.text:{15}} {token.pos_:{15}} {token.dep_:{15}} {token.head}')

if __name__ == "__main__":
    main()