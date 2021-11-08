import spacy # NLP Models

def main():
    nlp = spacy.load("models/01")
    nlp.add_pipe("ner")
    nlp.to_disk("models/01")

if __name__ == "__main__":
    main()