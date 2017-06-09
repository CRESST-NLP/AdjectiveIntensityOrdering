#!/usr/bin/env python3

import sys

import spacy

print(sys.version)
nlp = spacy.load('en')


def process(input):
    doc = nlp(input)
    print("| token | POS | head |")
    for token in doc:
        print(token, token.pos_, token.head)
        print("\t| child | POS | lemma |")
        for child in token.children:
            print("\t", child, child.pos_, child.lemma_)

            # text = nltk.word_tokenize(input)
            # print(text)
            # print(nltk.pos_tag(text))


if __name__ == '__main__':
    while True:
        input_term = input("\nEnter a phrase to parse (EXIT to break): ")
        if input_term == 'EXIT':
            break
        else:
            process(input_term)
