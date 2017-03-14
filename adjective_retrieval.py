#!/usr/bin/env python3

import csv
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


if __name__ == '__main__':
    # example:
    # > python adjective_retrieval.py temperature
    # Synset('cold.a.01')
    #   relation: temperature has_attribute
    #   Wiktionary: Having a low temperature.
    #   Oxford: "of or at a low or relatively low temperature, especially when compared with the human body:"
    # ```

    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    if len(sys.argv) != 2:
        sys.exit(0)

    property_name1 = sys.argv[1]
    with open('./data/adjective_retrieval_results.csv', 'w') as csvfile:
        fieldnames = ['Source', 'Relation', 'Word', 'WordNet Definition', 'Wikitionary Definition', 'Oxford Definition']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        synsets1 = get_attributes(property_name1)

        keywords1 = [property_name1]

        for synset1 in synsets1:
            keywords1.extend(get_keywords(synset1))

        for synset1 in synsets1:
            if not is_archaic(synset1):
                synset_name = get_name(synset1)

                wordnet_def = synset1.definition()
                try:
                    wiki_def = wiktionary_dict.get_most_likely_definition(wiki[synset_name]["A"], keywords1)
                except KeyError:
                    wiki_def = ""
                oxford_def = get_oxford_definition(synset_name, keywords1)

                writer.writerow({'Source': property_name1, 'Relation': 'has_attribute', 'Word': synset_name,
                                 'WordNet Definition': wordnet_def, 'Wikitionary Definition': wiki_def,
                                 'Oxford Definition': oxford_def})

                lemmas1 = get_lemmas(synset1)
                for lemma1 in lemmas1:
                    if lemma1 != synset_name:
                        try:
                            wiki_def1 = wiktionary_dict.get_most_likely_definition(wiki[lemma1]["A"], keywords1)
                        except KeyError:
                            wiki_def1 = ""
                        oxford_def1 = get_oxford_definition(lemma1, keywords1)

                        writer.writerow({'Source': synset_name, 'Relation': 'has_lemma', 'Word': lemma1,
                                 'WordNet Definition': wordnet_def, 'Wikitionary Definition': wiki_def1,
                                 'Oxford Definition': oxford_def1})

                similar_synsets1 = get_similar_synsets(synset1)
                for similar_synset1 in similar_synsets1:
                    if not is_archaic(similar_synset1):
                        similar_synset_name1 = get_name(similar_synset1)

                        wordnet_def1 = similar_synset1.definition()
                        try:
                            wiki_def2 = wiktionary_dict.get_most_likely_definition(wiki[similar_synset_name1]["A"], keywords1)
                        except KeyError:
                            wiki_def2 = ""
                        oxford_def2 = get_oxford_definition(similar_synset_name1, keywords1)

                        writer.writerow({'Source': synset_name, 'Relation': 'similar_tos', 'Word': similar_synset1,
                                 'WordNet Definition': wordnet_def1, 'Wikitionary Definition': wiki_def2,
                                 'Oxford Definition': oxford_def2})

                        lemmas2 = get_lemmas(similar_synset1)
                        for lemma2 in lemmas2:
                            if lemma2 != similar_synset_name1:
                                try:
                                    wiki_def3 = wiktionary_dict.get_most_likely_definition(wiki[lemma2]["A"], keywords1)
                                except KeyError:
                                    wiki_def3 = ""
                                oxford_def3 = get_oxford_definition(lemma2, keywords1)

                                writer.writerow({'Source': similar_synset1, 'Relation': 'has_lemma',
                                                 'Word': lemma2,
                                                 'WordNet Definition': wordnet_def1,
                                                 'Wikitionary Definition': wiki_def3,
                                                 'Oxford Definition': oxford_def3})