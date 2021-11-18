import utils

def main():
    outputFilePath = 'answer_gold_list.txt'

    # Load in list of paths 
    pathList = utils.load_data('answerTestList.txt')

    with open(outputFilePath, 'w') as outfile:
        for fname in pathList:
            with open(fname) as infile:
                outfile.write(infile.read())


if __name__ == "__main__":
    main()