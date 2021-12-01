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
import os
import re # Used for regex
import spacy # NLP Models
from spacy import displacy # Visualization Tools
from itertools import chain
from spacy.matcher import DependencyMatcher
from spacy import util # Filter Span


def get_first_verb(spn):
    root = spn.root
    head = root.head
    while head.pos_ != "VERB":
        prev_head = head
        head = head.head
        if head == prev_head:
            return None

    return head


def merge_docs(ml_doc, roberta_doc):
    acquire_words = ["acquire", "sell", "buy", "get", "take", "purchase"]
    dlramt_entities = [ent for ent in roberta_doc.ents if ent.label_ == "DLRAMT"]
    filtered_ents = []
    for ent in dlramt_entities:
        first_verb = get_first_verb(ent)
        if first_verb != None and first_verb.lemma_ in acquire_words:
            filtered_ents.append(ent)
    for ro_ent in filtered_ents:
        is_duplicate = False
        for ml_ent in [e for e in ml_doc.ents if e.label_ == "DLRAMT"]:
            if ro_ent.text == ml_ent.text:
                is_duplicate = True
                break
        if not is_duplicate:
            ml_doc.ents = [e for e in ml_doc.ents] + [ro_ent]

    return ml_doc


def main():
    sp = spacy.load("./models/06/model-best")
    roBERTa = spacy.load("./models/transformer")

    roBERTa_merged_entities = spacy.load("./models/transformer")
    roBERTa_merged_entities.add_pipe("merge_entities")
    
    dep_matcher = DependencyMatcher(vocab=roBERTa.vocab)
    dep_matcher_pronoun = DependencyMatcher(vocab=roBERTa.vocab)

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

    ruler = roBERTa.add_pipe("entity_ruler", before="ner")
    patterns = [
        {
            "label": "DLRAMT",
            "pattern": [
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["mln", "million", "billion"]}},
                {"LOWER": {"IN": ["dlrs", "dlr", "yen", "lire", "stg"]}}],
            "id": "dlramt"
        },
        {
            "label": "DLRAMT",
            "pattern": "undisclosed",
            "id": "dlramt"
        }
    ]
    ruler.add_patterns(patterns)

    dep_pattern = [{'RIGHT_ID': 'verb', 'RIGHT_ATTRS': {'POS': 'VERB'}},
               {'LEFT_ID': 'verb', 'REL_OP': '>', 'RIGHT_ID': 'subject', 'RIGHT_ATTRS': {'DEP': 'nsubj'}}
    ]

    dep_pattern_2 = [{'RIGHT_ID': 'verb', 'RIGHT_ATTRS': {'POS': 'VERB'}},
                    {'LEFT_ID': 'verb', 'REL_OP': '>', 'RIGHT_ID': 'subject', 'RIGHT_ATTRS': {'DEP': 'nsubj'}},
                    {'LEFT_ID': 'verb', 'REL_OP': '>', 'RIGHT_ID': 'd_object', 'RIGHT_ATTRS': {'DEP': 'dobj'}}
                    ]

    dep_pattern_3 = [{'RIGHT_ID': 'verb', 'RIGHT_ATTRS': {'POS': 'VERB'}},
               {'LEFT_ID': 'verb', 'REL_OP': ';*', 'RIGHT_ID': 'pronoun_before', 'RIGHT_ATTRS': {'POS': 'PROPN'}},
               {'LEFT_ID': 'verb', 'REL_OP': '.*', 'RIGHT_ID': 'pronoun_after', 'RIGHT_ATTRS': {'POS': 'PROPN'}}
    ]

    # Add the pattern to the matcher under the name 'nsubj_verb'
    dep_matcher.add('nsubj_verb', patterns=[dep_pattern])
    # Add the pattern to the matcher under the name 'nsubj_verb_dobj'
    dep_matcher.add('nsubj_verb_dobj', patterns=[dep_pattern_2])
    # Add the pattern to the matcher under the name 'pronoun_verb_pronoun'
    dep_matcher_pronoun.add('pronoun_verb', patterns=[dep_pattern_3])

    # Doclist of files to read in
    docFile = sys.argv[1]

    # Create empty list for file paths [PATH, FILENAME]
    pathList = list()

    # Directory paths for both docs and answer keys
    developmentDocs = '/data/development-docs'
    developmentKeys = '/data/development-anskeys'

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

        newDoc_merged_entities = roBERTa_merged_entities(documentText)
        newDoc = roBERTa(documentText)

        dep_matches = dep_matcher(newDoc_merged_entities)
        dep_matches_pronoun = dep_matcher_pronoun(newDoc_merged_entities)

        dependencyList = []
        pronounDependencyList = []

        for match in dep_matches_pronoun:
            matches = match[1]
            verb, pronoun_before, pronoun_after = matches[0], matches[1], matches[2]
            pronounDependencyList.append([newDoc_merged_entities[pronoun_before], newDoc_merged_entities[verb].lemma_, newDoc_merged_entities[pronoun_after]])
            # print(roBERTa.vocab[pattern_name].text, '\t', newDoc[pronoun_before], '...',  newDoc[verb].lemma_, '...',  newDoc[pronoun_after])

        # Loop over each tuple in the list 'dep_matches'
        for match in dep_matches:
            matches = match[1]
            if len(matches) > 2:
                verb, subject, dobject = matches[0], matches[1], matches[2]
                dependencyList.append([newDoc_merged_entities[subject], newDoc_merged_entities[verb], newDoc_merged_entities[dobject]])
                
            else:
                verb, subject = matches[0], matches[1]
                dependencyList.append([newDoc_merged_entities[subject], newDoc_merged_entities[verb]])
                # print(roBERTa.vocab[pattern_name].text, '\t', newDoc[subject], '...', newDoc[verb])

        print (f"TEXT: {path[1]}")
        entityList = []
        spacyEntityList = []
        
        # print("************************* MACHINE LEARNING MODEL *************************")
        # for ent in doc.ents:
            # entityList.append([ent.text, ent.label_])
            # print(f'{ent.text:{45}} {ent.label_}')

        # print("************************* SPACY TRANSFORMER MODEL *************************")
        for ent in newDoc.ents:
            spacyEntityList.append([ent.text, ent.label_])
            # if ent.label_ == 'GPE':
                # spacyEntityListLoc.append(ent.text)
            # print(f'{ent.text:{45}} {ent.label_}')
        
        # print("************************* MERGED *************************")
        merged = merge_docs(doc, newDoc)
        for ent in merged.ents:
            entityList.append([ent.text, ent.label_])
            # print(f'{ent.text:{45}} {ent.label_}')

        # TODO Uncomment when running in prod
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

        SELLER_BOOL = True

        if("SELLER" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'SELLER':
                    SELLER_BOOL = False
                    print (f"SELLER: \"{entity[0]}\"")
        
        elif("SELLER" not in chain(*entityList)):
            sellerList = []
            verbList = ['sell', 'move', 'close', 'trade', 'exchange', 'barter', 'give']
            for entity in spacyEntityList:
                usedEntityList = []
                for pronounList in pronounDependencyList:
                    strConversion = str(pronounList[0])
                    strVerb = str(pronounList[1])
                    if strConversion == entity[0] and entity[1] == 'ORG' and strVerb in verbList and entity[0] not in usedEntityList:
                        usedEntityList.append(entity[0])
                        SELLER_BOOL = False
                        sellerList.append(entity[0])
            if(len(sellerList)>0):
                print (f"SELLER: \"{sellerList[0]}\"")
        
        if(SELLER_BOOL):
            print (f"SELLER: ---")

        if("STATUS" in chain(*entityList)):
            for entity in entityList:
                if entity[1] == 'STATUS':
                    print (f"STATUS: \"{entity[0]}\"")
        
        elif("STATUS" not in chain(*entityList)):
           print (f"STATUS: ---") 

        print()

if __name__ == "__main__":
    main()