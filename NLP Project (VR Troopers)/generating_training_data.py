import os
import re # Used for regex
import spacy # NLP Models
from spacy import util # Filter Span
import random
from spacy.tokens import DocBin
from tqdm import tqdm
import utils

trainFileName = "aq_train_02.spacy"
validFileName = "aq_valid_02.spacy"
testFileName = "data/test_set.json"

random.seed(50)

def create_training(TRAIN_DATA):
    db = DocBin()
    nlp = spacy.blank("en")
    for text, annot in tqdm(TRAIN_DATA):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        pat_orig = len(ents)
        filtered = util.filter_spans(ents)
        pat_filt =len(filtered)

        # print("\nCONVERSION REPORT:")
        # print("Original number of patterns:", pat_orig)
        # print("Number of patterns after overlapping removal:", pat_filt)
        doc.ents = filtered
        db.add(doc)
    return (db)

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def main():
    # Directory paths for both docs and answer keys
    developmentDocs = '/data/development-docs'
    developmentKeys = '/data/development-anskeys'

    TRAIN_DATA = []
    docFileList = list()
    answerFileList = list()

    # Used for opening and reading all the files in the development docs
    for filename in os.listdir(os.getcwd() + developmentDocs):
        with open(os.path.join(os.getcwd() + developmentDocs, filename), 'r') as fileText: # open in readonly mode
            developmentDocText = fileText.read().replace("\n"," ").replace("  +"," ").strip()
            developmentDocText = re.sub(' +', ' ', developmentDocText)

            docFileList.append(developmentDocs[1:] + '/' + filename)
            answerFileList.append(developmentKeys[1:] + '/' + filename + ".key")

            with open(os.path.join(os.getcwd() + developmentKeys, filename + '.key'), 'r') as answerKeyText: # open in readonly mode
                developmentKeyText = answerKeyText.read().splitlines()
                entities = []

                for potentialMatch in developmentKeyText:
                    if(potentialMatch.find('"')!=-1):
                        counter = potentialMatch.count("/")
                        if counter == 0:
                            valueType = potentialMatch[:potentialMatch.find(":")]
                            valueText = potentialMatch[find_nth(potentialMatch, '"', 1)+1:find_nth(potentialMatch, '"', 2)]
                            # print(f'{valueType} {valueText} {developmentDocText.find(valueText)} {developmentDocText.find(valueText) + len(valueText)}')
                            entities.append([developmentDocText.lower().find(valueText.lower()), developmentDocText.lower().find(valueText.lower()) + len(valueText), valueType])
                        elif counter == 1:
                            valueType = potentialMatch[:potentialMatch.find(":")]
                            valueOneText = potentialMatch[potentialMatch.find('"')+1:potentialMatch.find('/')-2]
                            valueTwoText = potentialMatch[find_nth(potentialMatch, '"', 3)+1:find_nth(potentialMatch, '"', 4)]
                            # print(f'{valueType} {valueOneText} {valueTwoText}')
                            if(developmentDocText.lower().find(valueOneText.lower())!=-1):
                                entities.append([developmentDocText.lower().find(valueOneText.lower()), developmentDocText.lower().find(valueOneText.lower()) + len(valueOneText), valueType])
                            if(developmentDocText.lower().find(valueTwoText.lower())!=-1 and developmentDocText.lower().find(valueTwoText.lower())!=developmentDocText.lower().find(valueOneText.lower())):
                                entities.append([developmentDocText.lower().find(valueTwoText.lower()), developmentDocText.lower().find(valueTwoText.lower()) + len(valueTwoText), valueType])
                        elif counter == 2:
                            valueType = potentialMatch[:potentialMatch.find(":")]
                            valueOneText = potentialMatch[find_nth(potentialMatch, '"', 1)+1:find_nth(potentialMatch, '"', 2)]
                            valueTwoText = potentialMatch[find_nth(potentialMatch, '"', 3)+1:find_nth(potentialMatch, '"', 4)]
                            valueThreeText = potentialMatch[find_nth(potentialMatch, '"', 5)+1:find_nth(potentialMatch, '"', 6)]
                            # print(f'{valueType} {valueOneText} {valueTwoText}{valueThreeText}')
                            if(developmentDocText.lower().find(valueOneText.lower())!=-1):
                                entities.append([developmentDocText.lower().find(valueOneText.lower()), developmentDocText.lower().find(valueOneText.lower()) + len(valueOneText), valueType])
                            if(developmentDocText.lower().find(valueTwoText.lower())!=-1 and developmentDocText.lower().find(valueTwoText.lower())!=developmentDocText.lower().find(valueOneText.lower())):
                                entities.append([developmentDocText.lower().find(valueTwoText.lower()), developmentDocText.lower().find(valueTwoText.lower()) + len(valueTwoText), valueType])
                            if(developmentDocText.lower().find(valueThreeText.lower())!=-1 and developmentDocText.lower().find(valueThreeText.lower())!=developmentDocText.lower().find(valueOneText.lower()) and developmentDocText.lower().find(valueThreeText.lower())!=developmentDocText.lower().find(valueTwoText.lower())):
                                entities.append([developmentDocText.lower().find(valueThreeText.lower()), developmentDocText.lower().find(valueThreeText.lower()) + len(valueThreeText), valueType])
                TRAIN_DATA.append([developmentDocText, {"entities":entities}])

    mixed = list(zip(docFileList, answerFileList, TRAIN_DATA))

    random.shuffle(mixed)

    docFileList, answerFileList, TRAIN_DATA =  zip(*mixed)

    utils.save_data("data/aq_training_data.json", TRAIN_DATA)
    
    aq_train = create_training(TRAIN_DATA[0:299])
    aq_train.to_disk(trainFileName)

    aq_valid = create_training(TRAIN_DATA[300:349])
    aq_valid.to_disk(validFileName)

    utils.save_data(testFileName,TRAIN_DATA[350:])
    utils.save_data("document_testing_data.txt",docFileList[350:])
    utils.save_data("answer_testing_data.txt",answerFileList[350:])

if __name__ == "__main__":
    main()