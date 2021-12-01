import spacy # NLP Models

def main():
    nlp = spacy.load("./models/05")
    nlp.add_pipe("ner")
    nlp.to_disk("./models/05")

if __name__ == "__main__":
    main()