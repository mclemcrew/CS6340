import spacy # NLP Models

def main():
    nlp = spacy.load("models/03")
    nlp.add_pipe("ner")
    nlp.to_disk("models/03")

if __name__ == "__main__":
    main()