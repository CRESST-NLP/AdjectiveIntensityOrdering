#!/usr/bin/env python3

import spacy

# print(sys.version)
# nlp_en_core_web_sm = spacy.load('en_core_web_sm')
nlp_en_depent_web_md = spacy.load('en_depent_web_md')


def process(input):
    # doc = nlp_en_core_web_sm(input)
    # print('en_core_web_sm')
    # print("| token | POS | head |")
    # for token in doc:
    #     print(token, token.pos_, token.head)
    #     print("\t| child | POS | lemma |")
    #     for child in token.children:
    #         print("\t", child, child.pos_, child.lemma_)

    print('\nen_depent_web_md')
    doc2 = nlp_en_depent_web_md(input)
    print("| token | POS | head |")
    for token in doc2:
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
