import utils

def main():
    outputFilePath = 'answer_gold_list_v3.txt'

    # Load in list of paths 
    pathList = utils.load_data('answer_testing_data_v3.txt')

    with open(outputFilePath, 'w') as outfile:
        for fname in pathList:
            with open(fname) as infile:
                outfile.write(infile.read())


if __name__ == "__main__":
    main()