#!/usr/bin/env python3

import csv

import nltk
import numpy
from sklearn.decomposition import NMF
from sklearn.metrics.pairwise import cosine_similarity


def get_equation(definition):
    return


def order_words(file):
    adjectives, A = build_matrix(file)
    model = NMF(n_components=30)
    # A = W * H
    W = model.fit_transform(A)

    return (len(A[0]), len(W[0]))
    return sort_by_cosine_similarity(adjectives, W)


def build_matrix(file):
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        adjectives = []
        words = set()
        A = []

        for row in reader:
            adjectives.append(row['word'])
            text = nltk.word_tokenize(row['definition'].lower())
            word_pos_pair = nltk.pos_tag(text)
            for (word, pos) in word_pos_pair:
                if pos in {'NN', 'JJ', 'VB', 'RB'}:
                    words.add(word)

        words = list(words)
        words.sort()

        num_columns = len(words)
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)

        for row in reader:
            temp_row = [0] * num_columns
            context_words = row['definition'].lower().split()
            for context_word in context_words:
                if context_word in words:
                    index = words.index(context_word)
                    temp_row[index] += 1
            A.append(temp_row)

        return adjectives, A


def sort_by_cosine_similarity(adjectives, A):
    adjective_to_score = {adjectives[0]: 0}
    num_columns = len(A[0])
    for i in range(1, len(adjectives)):
        print(cosine_similarity(A[0], A[i]))
        adjective_to_score[adjectives[i]] = cosine_similarity(numpy.asarray(A[0]).reshape(1, num_columns),
                                                              numpy.asarray(A[i]).reshape(1, num_columns))

    adjective_score_pairs = [(word, adjective_to_score[word]) for word in adjective_to_score]
    adjective_score_pairs = sorted(adjective_score_pairs, key=lambda tup: tup[1])
    return adjective_score_pairs


if __name__ == '__main__':
    file = '/Users/Tan/Research/2016-2017/semantic-modeling/data/definitions.csv'
    print(order_words(file))
