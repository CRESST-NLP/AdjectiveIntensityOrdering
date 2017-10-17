#!/usr/bin/env python3

import csv
import sys
import bz2
import argparse

from nltk.corpus import wordnet as wn
import requests

import wiktionary_dict


def get_name(synset):
    return synset.name().split('.')[0]


def get_lemmas(synset):
    lemma_names = list(synset.lemma_names())
    return lemma_names


def get_adjectives(attribute):
    """
    Retrieves a attribute's adjectives from WordNet.
    :param attribute: A string containing an attribute i.e. "temperature".
    :return: An array containing the attribute's adjectives i.e. ["hot", "cold", "warm", "cool"].
    """
    synsets = wn.synsets(attribute, wn.NOUN)
    for synset in synsets:
        if synset.attributes():
            return synset.attributes()
    return []


def get_similar_synsets(synset):
    """
    Retrieves a synset's similar synsets according to WordNet.
    :param synset: a WordNet synset.
    :return: an array containing similar synsets from WordNet.
    ex:
        input: Synset('hot.a.01')
        output: [Synset('baking.s.01'), Synset('blistering.s.02'), Synset('calefacient.s.01'),
            Synset('calefactory.s.01'), Synset('calorifacient.s.01'), Synset('calorific.s.01'),
            Synset('fervent.s.02'), Synset('fiery.s.02'), Synset('heatable.s.01'), Synset('heated.s.01'),
            Synset('hottish.s.01'), Synset('overheated.s.01'), Synset('red-hot.s.04'), Synset('scorching.s.01'),
            Synset('sizzling.s.01'), Synset('sultry.s.02'), Synset('sweltering.s.01'), Synset('thermal.s.03'),
            Synset('torrid.s.03'), Synset('tropical.s.04'), Synset('white.s.06')]
    """
    return synset.similar_tos()


def filter_archaic_synsets(synsets):
    """
    Filters archaic synsets out of an array of synsets.
    :param synsets: an array containing WordNet synsets.
    :return: an array with archaic synsets removed.
    """
    archaism = wn.synsets("archaism")[0]
    results = []
    for synset in synsets:
        if archaism in synset.usage_domains():
            continue
        else:
            results.append(synset)
    return results


def get_synsets_with_wordnet_extended(attribute):
    """
    Retrieves an attribute's adjective synsets and similar synsets from WordNet.
    :param attribute: A string containing an attribute i.e. "temperature".
    :return: An array containing the attribute's adjectives and similar synsets.
    """
    synsets = get_adjectives(attribute)
    result = list(synsets)
    for synset in synsets:
        result.extend(get_similar_synsets(synset))
    return result


def get_oxford_definition(word, keywords=[], pos='a'):
    """
    Retrieves a word's definition from Oxford Dictionary.
    :param pos: A string specifying the word's part of speech.
    :return: A string containing the word's definition.
    """
    # wn.NOUN = 'n'
    # wn.VERB = 'v'
    # wn.ADJ = 'a'
    # wn.ADV = 'r'

    if pos != wn.NOUN and pos != wn.VERB and pos != wn.ADJ and pos != wn.ADV:
        print("Invalid part of speech: " + pos + ". Expected 'n', 'v', 'a', or 'r'.")
        return ""

    if pos == 'n':
        lexical_category = "Noun"
    elif pos == 'v':
        lexical_category = "Verb"
    elif pos == 'a':
        lexical_category = "Adjective"
    else:
        lexical_category = "Adverb"

    app_id = '4763721e'
    app_key = 'c019d50f24fc6f3d53ea53d7f9f0e983'

    language = 'en'

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word.lower()
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})

    result = ""
    if r.status_code == 200:
        lexical_entries = r.json()["results"][0]["lexicalEntries"]
        for lexical_entry in lexical_entries:
            try:
                if lexical_entry["lexicalCategory"] == lexical_category:
                    senses = lexical_entry["entries"][0]["senses"]
                    for sense in senses:
                        if result == "":
                            result = sense["definitions"][0]
                        else:
                            for keyword in keywords:
                                curr_definition = sense["definitions"][0]
                                if keyword in curr_definition:
                                    result = curr_definition
                                    return result
                        subsenses = sense["subsenses"]
                        for subsense in subsenses:
                            if result == "":
                                result = subsense["definitions"][0]
                            else:
                                for keyword in keywords:
                                    curr_definition = subsense["definitions"][0]
                                    if keyword in curr_definition:
                                        result = curr_definition
                                        return result
            except KeyError:
                continue

    return result


def is_archaic(synset):
    archaism = wn.synsets("archaism")[0]
    return archaism in synset.usage_domains()


def get_most_likely_wordnet_definition(adjective, keywords):
    result = ""
    for synset in wn.synsets(adjective, wn.ADJ):
        definition = synset.definition()
        if result == "":
            result = definition
        else:
            for word in definition:
                if word in keywords:
                    result = definition
                    return result
    return result


def get_keywords(synset):
    keywords = [get_name(synset)]
    if not is_archaic(synset):
        lemmas = get_lemmas(synset)
        keywords.extend(lemmas)
        similar_synsets = get_similar_synsets(synset)
        for similar_synset in similar_synsets:
            if not is_archaic(similar_synset):
                similar_synset_name = get_name(similar_synset)
                keywords.append(similar_synset_name)
                lemmas2 = get_lemmas(similar_synset)
                keywords.extend(lemmas2)
    return keywords


def retrieve_definitions(attribute, wiktionary_path, output_path=None):
    """
    Creates a file called [attribute]_definitions.csv with WordNet, Wikitionary, and Oxford definitions.
    :param attribute: A string containing an attribute i.e. "temperature".
    :param wiktionary_path: Path to 2011-08-01_OntoWiktionary_EN.xml.bz2
    :param output_path: Optional path to output csv file. Defaults to `attribute`_definitions.csv
    """
    wiki = wiktionary_dict.load_ontology(bz2.open(wiktionary_path))

    if output_path:
        csv_path = output_path
    else:
        csv_path = attribute + '_definitions.csv'
    with open(csv_path, 'w') as csvfile:
        fieldnames = ['Source', 'Relation', 'Word', 'WordNet Definition', 'Wiktionary Definition', 'Oxford Definition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        synsets = get_adjectives(attribute)

        keywords = [attribute]

        for synset in synsets:
            keywords.extend(get_keywords(synset))

        for synset in synsets:
            if not is_archaic(synset):
                synset_name = get_name(synset)

                wordnet_def = synset.definition()
                try:
                    wiki_def = wiktionary_dict.get_most_likely_definition(wiki[synset_name]["A"], keywords)
                except KeyError:
                    wiki_def = ""
                oxford_def = get_oxford_definition(synset_name, keywords)

                writer.writerow({'Source': attribute, 'Relation': 'has_attribute', 'Word': synset_name,
                                 'WordNet Definition': wordnet_def, 'Wiktionary Definition': wiki_def,
                                 'Oxford Definition': oxford_def})

                # add lemmas
                lemmas = get_lemmas(synset)
                for lemma in lemmas:
                    if lemma != synset_name:
                        try:
                            wiki_def = wiktionary_dict.get_most_likely_definition(wiki[lemma]["A"], keywords)
                        except KeyError:
                            wiki_def = ""
                        oxford_def = get_oxford_definition(lemma, keywords)

                        writer.writerow({'Source': synset_name, 'Relation': 'has_lemma', 'Word': lemma,
                                         'WordNet Definition': wordnet_def, 'Wiktionary Definition': wiki_def,
                                         'Oxford Definition': oxford_def})

                # add similar synsets
                similar_synsets = get_similar_synsets(synset)
                for similar_synset in similar_synsets:
                    if not is_archaic(similar_synset):
                        similar_synset_name = get_name(similar_synset)

                        wordnet_def = similar_synset.definition()
                        try:
                            wiki_def = wiktionary_dict.get_most_likely_definition(wiki[similar_synset_name]["A"],
                                                                                  keywords)
                        except KeyError:
                            wiki_def = ""
                        oxford_def = get_oxford_definition(similar_synset_name, keywords)

                        writer.writerow({'Source': synset_name, 'Relation': 'similar_tos', 'Word': similar_synset_name,
                                         'WordNet Definition': wordnet_def, 'Wiktionary Definition': wiki_def,
                                         'Oxford Definition': oxford_def})

                        # add similar synsets' lemmas
                        lemmas = get_lemmas(similar_synset)
                        for lemma in lemmas:
                            if lemma != similar_synset_name:
                                try:
                                    wiki_def = wiktionary_dict.get_most_likely_definition(wiki[lemma]["A"], keywords)
                                except KeyError:
                                    wiki_def = ""
                                oxford_def3 = get_oxford_definition(lemma, keywords)

                                writer.writerow({'Source': similar_synset_name, 'Relation': 'has_lemma',
                                                 'Word': lemma,
                                                 'WordNet Definition': wordnet_def,
                                                 'Wiktionary Definition': wiki_def,
                                                 'Oxford Definition': oxford_def3})


if __name__ == '__main__':
    # example:
    # > python3 temperature
    # creates the file temperature_definitions.csv or overwrites existing file

    parser = argparse.ArgumentParser()
    parser.add_argument("input_term", help='A string containing an attribute i.e. "temperature"')
    parser.add_argument("--wiktionary", help="Path to 2011-08-01_OntoWiktionary_EN.xml.bz2", type=str, default="./data/2011-08-01_OntoWiktionary_EN.xml.bz2")
    args = parser.parse_args()

    retrieve_definitions(args.input_term, args.wiktionary)
