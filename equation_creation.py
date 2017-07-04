#!/usr/bin/env python3

import collections
import csv
import re
import sys

import spacy
from nltk.stem.porter import PorterStemmer
from PyDictionary import PyDictionary

from score import intensifiers, downtoners, adj_intensity_map

dictionary = PyDictionary()
nlp = spacy.load("en_depent_web_md")


def get_csv_column(column_name, csv_file_path):
    """

    :param column_name: a string containing a field name from the csv file
    :param csv_file_path: a string containing a path to a csv file
    :return: an OrderedDict containing the contents of the column in the csv file
    """
    variables = collections.OrderedDict([])
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            variables.update({row[column_name]: ""})
    return variables


def create_equations(property_name, equations_csv_path, definitions_csv_path):
    """

    :param property_name: a string containing the name of the property
    :param equations_csv_path: a string containing a path to a csv file to write the equations to
    :param definitions_csv_path: a string containing a path to a csv file containing the adjectives and definitions
    :return:
    """
    words = get_csv_column('Word', definitions_csv_path)
    words.update({"high_prop": ""})

    with open(equations_csv_path, 'w') as equations_file, open(definitions_csv_path, 'r') as definitions_file:
        fieldnames = ['Word', 'Variable', 'Factor', 'Definition', "Deduced"]
        writer = csv.DictWriter(equations_file, fieldnames=fieldnames)
        writer.writeheader()

        reader = csv.DictReader(definitions_file)
        for row in reader:
            definitions = []
            definitions.extend(row['WordNet Definition'].lower().split(';'))
            definitions.extend(row['Wikitionary Definition'].lower().split(';'))
            definitions.extend(row['Oxford Definition'].lower().split(';'))
            word = row['Word']
            for definition in definitions:
                definition = combine_words(definition, "not", "quite")
                doc = nlp(definition)
                noun_scores = get_noun_scores(doc, property_name)
                adj_adv_scores = get_adj_adv_scores(word, doc, property_name, words)

                for score in noun_scores:
                    writer.writerow({'Word': word, 'Variable': 'high_prop', 'Factor': str(score),
                                     'Definition': definition})
                    writer.writerow({'Word': "high_prop", 'Variable': word, 'Factor': str(1.0 / score),
                                     'Definition': definition, 'Deduced': 'Yes'})
                for (a, score) in adj_adv_scores:
                    writer.writerow({'Word': word, 'Variable': a, 'Factor': str(score),
                                     'Definition': definition})
                    writer.writerow({'Word': a, 'Variable': word, 'Factor': str(1.0 / score),
                                     'Definition': definition, 'Deduced': 'Yes'})


def combine_words(text, a, b):
    """
    This function is needed b/c spacy doesn't parse phrases like "not quite" correctly
    :return: A string combining adjacent words a b in text to form a_b in new_text
    """
    text = text.split()
    new_text = []
    i = 0
    while i < len(text) - 1:
        if text[i] == a and text[i + 1] == b:
            new_text.append(a + "_" + b)
            i += 2
        else:
            new_text.append(text[i])
            i += 1

    if i < len(text) and text[i] != "quite":
        new_text.append(text[i])

    return " ".join(new_text)


def get_noun_scores(doc, property_name):
    synonyms = dictionary.synonym(property_name)
    scores = []
    for token in doc:
        if token.tag_ == "NN" and (token.text == property_name or token.text in synonyms):
            added = False
            modified_by_adj = False
            for child in token.children:
                if child.text in adj_intensity_map:
                    modified_by_adj = True
                    for grandchild in child.children:
                        if grandchild.text in intensifiers:
                            added = True
                            scores.append(adj_intensity_map[child.text] * intensifiers[grandchild.text])
                        elif grandchild.text in downtoners:
                            added = True
                            scores.append(adj_intensity_map[child.text] * downtoners[grandchild.text])
                    if not added:
                        scores.append(adj_intensity_map[child.text])
            if not modified_by_adj:
                scores.append(1)
    return scores


def get_adj_adv_scores(current_word, doc, property_name, other_words):
    scores = []
    definition_array = re.findall(r"[\w]+", doc.text)
    for token in doc:
        try:
            curr_i = definition_array.index(token.text)
        except ValueError:
            curr_i = -1
        if (token.tag_ == "JJ" or token.tag_ == "RB") and token.head.text != property_name:
            matches = find_links(current_word, token.text, other_words)
            if matches is not None:
                found_adverb = False
                for child in token.children:
                    if child.text not in definition_array:
                        continue
                    child_i = definition_array.index(child.text)
                    if child.text in intensifiers:
                        for match in matches:
                            if child_i > 0 and (definition_array[child_i - 1] == "neither" or
                                                        definition_array[child_i - 1] == "nor" or
                                                        definition_array[child_i - 1] == "not"):
                                scores.append((match, -intensifiers[child.text]))
                            else:
                                scores.append((match, intensifiers[child.text]))
                        found_adverb = True
                    elif child.text in downtoners:
                        for match in matches:
                            if child_i > 0 and (definition_array[child_i - 1] == "neither" or
                                                        definition_array[child_i - 1] == "nor" or
                                                        definition_array[child_i - 1] == "not"):
                                scores.append((match, -downtoners[child.text]))
                            else:
                                scores.append((match, downtoners[child.text]))
                        found_adverb = True
                    elif child.text == "not" or child.text == "neither" or child.text == "nor":
                        for match in matches:
                            scores.append((match, -1))
                        found_adverb = True
                if not found_adverb:
                    for match in matches:
                        if curr_i > 0 and (definition_array[curr_i - 1] == "neither" or
                                                   definition_array[curr_i - 1] == "nor" or
                                                   definition_array[curr_i - 1] == "not"):
                            scores.append((match, -1))
                        else:
                            scores.append((match, 1))
    return scores


def find_links(current_word, definition_word, other_words):
    links = []
    porter_stemmer = PorterStemmer()
    definition_word_stem = porter_stemmer.stem(definition_word)
    for other_word in other_words:
        if other_word == current_word:
            continue
        other_word_stem = porter_stemmer.stem(other_word)
        if definition_word_stem == other_word_stem:
            links.append(other_word)
    return links


if __name__ == '__main__':
    # example:
    # > python3 equation_creation.py temperature

    if len(sys.argv) != 2:
        sys.exit(0)

    input_term = sys.argv[1]

    equations_file = "/Users/Tan/Research/2016-2017/semantic-modeling/data/" + input_term + "_equations.csv"
    definitions_file = "/Users/Tan/Research/2016-2017/semantic-modeling/data/" + input_term + "_definitions.csv"

    create_equations(input_term, equations_file, definitions_file)
