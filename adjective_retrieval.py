#!/usr/bin/env python3

import json
import sys
import bz2

from nltk.corpus import wordnet as wn
import requests

import wiktionary_dict


def get_name(synset):
    return synset.name().split('.')[0]


def get_lemmas(synset):
    lemma_names = list(synset.lemma_names())
    return lemma_names


def get_attributes(property_name):
    """
    Retrieves a property_name's attributes from WordNet's attributes
    :param property_name: A string i.e. "temperature"
    :return: An array containing the property_name's attributes i.e. ["hot", "cold", "warm", "cool"]
    """
    synsets = wn.synsets(property_name, wn.NOUN)
    for synset in synsets:
        if synset.attributes():
            return synset.attributes()
    return []


def get_similar_synsets(synset):
    """
    Retries a synset's similar synsets according to WordNet.
    :param synset: a synset
    :return: an array containing similar synsets.
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

    :param synsets: an array consisting of WordNet synsets.
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


def get_synsets_with_wordnet_attributes_extended(property_name):
    """
    Retrieves a property's attributes from WordNet's attributes and words similar to the attributes
    :param property_name: A string
    :return: An array containing the property's attributes and the attributes' similar synsets
    """
    synsets = get_attributes(property_name)
    result = list(synsets)
    for synset in synsets:
        result.extend(get_similar_synsets(synset))
    return result


def get_oxford_definition(word, keywords=[], pos='a'):
    """
    Retrieves a word's definition from Oxford Dictionary
    :param property: A word i.e. "temperature"
    :param pos: A string specifying the parts of speech to search for the word's attributes
    :return: A string containing the definition of the word
    """
    # wn.NOUN = 'n'
    # wn.VERB = 'v'
    # wn.ADJ = 'a'
    # wn.ADV = 'r'

    if pos != wn.NOUN and pos != wn.VERB and pos != wn.ADJ and pos != wn.ADV:
        return ""
        print("Invalid part of speech: " + pos + ". Expected 'n', 'v', 'a', or 'r'.")

    if pos == 'n':
        lexical_category = "Noun"
    elif pos == 'v':
        lexical_category = "Verb"
    elif pos == 'a':
        lexical_category = "Adjective"
    else:
        lexical_category = "Adverb"

    app_id = '***REMOVED***'
    app_key = '***REMOVED***'

    language = 'en'

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word.lower()
    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

    result = ""
    if r.status_code == 200:
        lexical_entries = r.json()["results"][0]["lexicalEntries"]
        for lexical_entry in lexical_entries:
            try:
                if lexical_entry["lexicalCategory"] == lexical_category:
                    if result == "":
                        result = lexical_entry["entries"][0]["senses"][0]["definitions"][0]
                    for keyword in keywords:
                        if keyword in result:
                            result = lexical_entry["entries"][0]["senses"][0]["definitions"][0]
                            return result
            except KeyError:
                continue

    return result


def is_archaic(synset):
    archaism = wn.synsets("archaism")[0]
    return archaism in synset.usage_domains()


def print_definitions(word, keywords):
    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    try:
        wiki_def = wiktionary_dict.getMostLikelyDefinition(wiki[word]["A"], keywords)
        print("\tWiktionary:", wiki_def)
    except KeyError:
        print("\tWiktionary:")

    print("\tOxford:", json.dumps(get_oxford_definition(word, keywords)))

if __name__ == '__main__':
    # example:
    # > python adjective_retrieval.py temperature
    # Synset('cold.a.01')
    #   relation: temperature has_attribute
    #   Wiktionary: Having a low temperature.
    #   Oxford: "of or at a low or relatively low temperature, especially when compared with the human body:"
    # ```

    if len(sys.argv) < 2:
        sys.exit(0)

    for property_name1 in sys.argv[1:]:
        synsets1 = get_attributes(property_name1)
        keywords1 = [property_name1] + [get_name(synset1) for synset1 in synsets1]

        for synset1 in synsets1:
            if not is_archaic(synset1):
                # print(synset1)
                # print("\trelation:", property_name1, "has_attribute")
                synset_name = get_name(synset1)

                # print_definitions(synset_name, keywords)

                lemmas1 = get_lemmas(synset1)
                keywords1.extend(lemmas1)

                for lemma1 in lemmas1:
                    if lemma1 != synset_name:
                        print(lemma1)
                        print("\trelation:", synset_name, "has_lemma")
                        print_definitions(lemma1, keywords1)

                similar_synsets1 = get_similar_synsets(synset1)
                for similar_synset1 in similar_synsets1:
                    if not is_archaic(similar_synset1):
                        print(similar_synset1)
                        similar_synset_name = get_name(similar_synset1)
                        print("\trelation:", synset_name, "similar_tos")

                        keywords1.append(similar_synset_name)

                        print_definitions(similar_synset_name, keywords1)

                        lemmas2 = get_lemmas(similar_synset1)
                        keywords1.extend(lemmas2)

                        for lemma2 in lemmas2:
                            if lemma2 != similar_synset_name:
                                print(lemma2)
                                print("\trelation:", similar_synset_name, "has_lemma")
                                print_definitions(lemma2, keywords1)
            print("\n")
