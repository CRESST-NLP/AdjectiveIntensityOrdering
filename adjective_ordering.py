#!/usr/bin/env python3

import numpy as np
import pandas as pd
import spacy

from adjective_and_definition_retrieval import *
from score import get_score_with_spacy as get_score

nlp = spacy.load("en")

# irrelevant_adj = ["raw", "polar", "cutting", "nipping", "snappy", "refrigerant", "refrigerating", "refrigerated",
#                   "shivery", "caller", "precooled", "water-cooled", "warming", "fervent", "baking_hot", "blistery",
#                   "calefacient", "calefactory", "calefactive", "calorifacient", "calorific", "heatable", "heated_up",
#                   "het", "het_up", "sulfurous", "sulphurous", "sweltry", "white", "white-hot", "fervid"]

irrelevant_adj = ["accelerated", "double-quick", "fast-breaking", "high-velocity", "hot", "hurrying", "lazy",
                  "long-play", "long-playing", "pokey", "red-hot", "scurrying", "slow-moving",
                  "sulky"]

HQ = 1
LQ = -1


def order_adjectives_by_definition(csvfile):
    # definitions = {}
    # # open csv with words and definitions
    # with open('./data/definitions.csv') as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         definition = row['definition'].lower()
    #         definitions[row['word']] = definition
    #
    # equations = {}
    # # add words and definitions as needed
    # # create equations from the definitions
    # for word in definitions:
    #     definition = definitions[word]
    #     doc = nlp(definition)
    #     for word in doc:
    #         if word.tag_ == "JJ" or word.tag_ == "NN" or word.text == property_name:
    #             if word in definitions or word in score.intensifiers or word in score.downtoners or word in score.adj_intensity_map:
    #                 continue
    #             else:
    #
    # create matrix A from word equations
    # words = sorted(equations.keys()) + ['HT']
    # A = get_matrix(words, word_to_equations)

    words = pd.read_csv(csvfile).word.tolist()
    print(words)
    A = build_matrix(words, csvfile)
    print(A)

    size = len(words)
    b = np.array([0] * (size - 1) + [10])

    # find the least squares
    x = np.round(np.linalg.lstsq(A, b)[0], 2)
    word_score_tuples = list(zip(words, x))

    # sort the attributes
    sorted_word_score_tuples = sorted(word_score_tuples, key=lambda tup: tup[1])
    return sorted_word_score_tuples


def build_matrix(words, csvfile_name):
    A = []

    adverb_scores = {"not quite": 0.1, "slightly": 0.2, "mildly": 0.2, "pleasantly": 0.3, "moderately": 0.5,
                     "moderate": 0.5, "rather": 0.5, "somewhat": 0.5, "mild": 0.8, "excessively": 1.4, "excessive": 1.4,
                     "considerably": 1.4, "very": 2, "extremely": 2, "extreme": 2, "completely": 2, "not": -1,
                     "lacking": -1}

    with open(csvfile_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            arr = [0] * len(words)
            word = row['word']
            arr[words.index(word)] = 1
            equation1 = row['equation1']
            if equation1 != "":
                factor = row['equation1_factor']
                if factor != "":
                    arr[words.index(row['equation1'])] = adverb_scores[row['equation1_factor']] * -1
                else:
                    arr[words.index(row['equation1'])] = -1
            equation2 = row['equation2']
            if equation2 != "":
                factor = row['equation2_factor']
                if factor != "":
                    arr[words.index(row['equation2'])] = adverb_scores[row['equation2_factor']] * -1
                else:
                    arr[words.index(row['equation2'])] = -1
            equation3 = row['equation3']
            if equation3 != "":
                factor = row['equation3_factor']
                if factor != "":
                    arr[words.index(row['equation3'])] = adverb_scores[row['equation3_factor']] * -1
                else:
                    arr[words.index(row['equation3'])] = -1
            A.append(arr)
    return A


def get_matrix(words, word_equations_map):
    """
    create matrix from word equations

    :param words: list of words
    :param word_equations_map: dictionary mapping from word to array of equations
        ex: { frigid: [(cold, 1.4), (warmth, -1), (icy, 1)]
    :return: array of arrays (with dimension # of equations x # of words)
    """
    matrix = []
    for word in word_equations_map:
        for tuple in word_equations_map[word]:
            arr = [0] * len(words)
            arr[words.indexOf(word)] = -1
            arr[words.indexOf(tuple[0])] = tuple[1]
            matrix.append(arr)
    return matrix


def order_synsets(property_name, synsets, keywords, default_score=0):
    """

    :param property_name: A string containing the name of the property of the attributes contained in adjectives.
    :param synsets: An array of strings containing adjective synsets that attributes of the same property.
    :param keywords: An array of strings for helping to find the correct word sense by looking for the keyword in the
                     adjective definitions.
    :return: An array of (string, float) pairs containing adjectives and scores in order of increasing score.

    ex: input:
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
            keywords: [temperature, cold, cool, hot, warm]
        output:
            [(Synset('cold.a.01'), -1.0), (Synset('cool.a.01'), 0.6), (Synset('warm.a.01'), 0.6), (Synset('hot.a.01'), 1.0)]
    """
    synset_score_pairs = []

    for s in synsets:
        score = get_score(property_name, get_name(s), keywords, default_score)
        if score is not None:
            synset_score_pairs.append((s, score))

    sorted_synset_to_score = sorted(synset_score_pairs, key=lambda tup: tup[1])
    return sorted_synset_to_score


def order_adjectives_extended_with_lemma_definitions(property_name, ordered_synsets):
    """
    Returns a list of ordered adjectives using similar words and lemmas from WordNet.
    Uses Wiktionary definition. If no wiktionary definiton exists, uses WordNet definitions.

    :param property_name: A string containing the name of the property of the words in the ordered_synsets.
    :param ordered_synsets: An array of (Synset, float) pairs, where the second item is the score in order of
            increasing score.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.
    """
    result = []
    seen_words = set()

    keywords = []
    for synset in ordered_synsets:
        keywords.extend(get_keywords(synset))

    for (synset, score) in ordered_synsets:
        adjective = get_name(synset)
        similar_synsets = filter_archaic_synsets(get_similar_synsets(synset))
        lemmas = get_lemmas(synset)
        for word in lemmas:
            seen_words.add(word)
        if lemmas is None:
            lemmas = []
        for similar_synset in similar_synsets:
            for word in get_lemmas(similar_synset):
                if word in seen_words:
                    continue
                else:
                    if word not in irrelevant_adj:
                        lemmas.append(word)
                        seen_words.add(word)
        lemmas.remove(adjective)  # don't recalculate score for synset; avoids using wrong word sense

        for lemma in lemmas:
            # result.append((lemma, get_score(property_name, lemma, keywords, score)))
            result.append((lemma, get_score(property_name, lemma, keywords, 0)))

        result.append((adjective, score))

    return sorted(result, key=lambda tup: tup[1])


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     sys.exit(0)

    # with open('./data/temperature.csv', 'w') as csvfile:
    # writer = csv.writer(csvfile)
    #
    # property_name = sys.argv[1]
    # synsets = filter_archaic_synsets(get_attributes(property_name))
    # attributes = [get_name(synset) for synset in synsets]
    # ordered_synsets = order_synsets(property_name, synsets, [property_name] + attributes)
    #
    # orderedAdjectivesExtended = order_adjectives_extended_with_lemma_definitions(property_name, ordered_synsets)
    # print(orderedAdjectivesExtended)
    # writer.writerow(orderedAdjectivesExtended)
    print(order_adjectives_by_definition('./data/word_to_equations.csv'))
