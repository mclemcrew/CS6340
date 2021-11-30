import spacy # NLP Models

def main():
    nlp = spacy.load("en_core_web_trf")
    # nlp.add_pipe("ner")
    nlp.to_disk("models/transformer")

if __name__ == "__main__":
    main()