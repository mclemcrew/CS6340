import json
from gensim.models.word2vec import Word2Vec
from gensim.models.keyedvectors import KeyedVectors
import multiprocessing
import utils
import os
import re
import spacy

developmentDocs = '/data/development-docs'
wordVecLocation = 'data/word_vectors_training_data.json'

def build_training_data():
    WORD_VEC_DATA = []
    sp = spacy.load('en_core_web_trf') # roBERTa model load

    all_stopwords = sp.Defaults.stop_words # Get all stop words
    all_stopwords.add("Reuter") # Add forms for Reuter
    all_stopwords.add("reuter")
    all_stopwords.add("REUTER")
    all_stopwords.remove("in") # This is included in some status forms
    all_stopwords.remove("for") # This is included in some status forms
    all_stopwords.remove("the") # This is included in some status forms

    for filename in os.listdir(os.getcwd() + developmentDocs):
        with open(os.path.join(os.getcwd() + developmentDocs, filename), 'r') as fileText: # open in readonly mode
            DOC_TOKEN_DATA = []
            developmentDocText = fileText.read().replace("\n"," ").replace("  +"," ").strip()

            big_regex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, all_stopwords)))
            developmentDocText = big_regex.sub("", developmentDocText)

            developmentDocText = re.sub(' +', ' ', developmentDocText)

            doc = sp(developmentDocText)

            for token in doc:
                if token.text == '.' or token.text == '?' or token.text == '!' or token.text == ',' or token.text == '\"' or token.text == '-' or token.text == '(' or token.text == ')':
                    continue
                else:
                    DOC_TOKEN_DATA.append(token.text)
            WORD_VEC_DATA.append(DOC_TOKEN_DATA)
    utils.save_data(wordVecLocation,WORD_VEC_DATA)

# build_training_data()

def training(model_name):
    texts = utils.load_data(wordVecLocation)
    sentences = texts
    cores = multiprocessing.cpu_count()
    w2v_model = Word2Vec(
        min_count = 1,
        window = 2,
        vector_size = 500,
        sample=6e-5,
        alpha=0.03,
        min_alpha=0.0007,
        negative=20,
        workers=cores-1
    )
    w2v_model.build_vocab(texts)
    w2v_model.train(texts,total_examples = w2v_model.corpus_count, epochs=30)
    w2v_model.save(f"word2vec/{model_name}.model")
    w2v_model.wv.save_word2vec_format(f"word2vec/word2vec_{model_name}.txt")

def gen_similarity(word):
    model = KeyedVectors.load_word2vec_format("",binary = False)
    results = model.most_similar(positive=[word])
    print(results)

# Might want to try and remove more stop words....unsure
training('aq_ner_model_00')