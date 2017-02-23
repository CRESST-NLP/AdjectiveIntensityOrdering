#!/usr/bin/env python3

import json
import sys
import bz2

from nltk.corpus import wordnet as wn
import requests

import wiktionary_dict


def getName(synset):
    return synset.name().split('.')[0]


def getLemmas(synset):
    return synset.lemma_names()


def getAttributes(property):
    """
    Retrieves a property's attributes from WordNet's attributes
    :param property: A string i.e. "temperature"
    :return: An array containing the property's attributes i.e. ["hot", "cold", "warm", "cool"]
    """
    synsets = wn.synsets(property, wn.NOUN)
    for synset in synsets:
        if synset.attributes() != []:
            return synset.attributes()
    return []


def getSimilarSynsets(synset):
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


def filterArchaicSynsets(synsets):
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


def getSynsetsWithWordNetAttributesExtended(propertyName):
    """
    Retrieves a property's attributes from WordNet's attributes and words similar to the attributes
    :param propertyName: A string
    :return: An array containing the property's attributes and the attributes' similar synsets
    """
    synsets = getAttributes(propertyName)
    result = set(synsets)
    for synset in synsets:
        result.update(getSimilarSynsets(synset))
    return result


def getOxfordDefinition(word, keywords=[], pos='a'):
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
        lexicalCategory = "Noun"
    elif pos == 'v':
        lexicalCategory = "Verb"
    elif pos == 'a':
        lexicalCategory = "Adjective"
    else:
        lexicalCategory = "Adverb"

    app_id = '4763721e'
    app_key = 'c019d50f24fc6f3d53ea53d7f9f0e983'

    language = 'en'

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word.lower()
    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

    result = ""
    if r.status_code == 200:
        lexicalEntries = r.json()["results"][0]["lexicalEntries"]
        for lexicalEntry in lexicalEntries:
            try:
                if lexicalEntry["lexicalCategory"] == lexicalCategory:
                    if result == "":
                        result = lexicalEntry["entries"][0]["senses"][0]["definitions"][0]
                    for keyword in keywords:
                        if keyword in result:
                            result = lexicalEntry["entries"][0]["senses"][0]["definitions"][0]
                            return result
            except KeyError:
                continue

    return result


def isArchaic(synset):
    archaism = wn.synsets("archaism")[0]
    return archaism in synset.usage_domains()


def printDefinitions(word, keywords):
    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    try:
        wiki_def = wiktionary_dict.getMostLikelyDefinition(wiki[word]["A"], keywords)
        print("\tWiktionary:", wiki_def)
    except KeyError:
        print("\tWiktionary:")

    print("\tOxford:", json.dumps(getOxfordDefinition(word, keywords)))

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

    for propertyName in sys.argv[1:]:
        synsets = getAttributes(propertyName)
        keywords = [propertyName] + [getName(synset) for synset in synsets]

        for synset in synsets:
            if not isArchaic(synset):
                print(synset)
                print("\trelation:", propertyName, "has_attribute")
                synsetName = getName(synset)

                printDefinitions(synsetName, keywords)

                lemmas = getLemmas(synset)
                keywords += lemmas

                for lemma in lemmas:
                    if lemma != synsetName:
                        print(lemma)
                        print("\trelation:", synsetName, "has_lemma")
                        printDefinitions(lemma, keywords)

                similarSynsets = getSimilarSynsets(synset)
                for similarSynset in similarSynsets:
                    if not isArchaic(similarSynset):
                        print(similarSynset)
                        similarSynsetName = getName(similarSynset)
                        print("\trelation:", synsetName, "similar_tos")

                        keywords += [similarSynsetName]

                        printDefinitions(similarSynsetName, keywords)

                        lemmas = getLemmas(similarSynset)
                        keywords += lemmas

                        for lemma in lemmas:
                            if lemma != similarSynsetName:
                                print(lemma)
                                print("\trelation:", similarSynsetName, "has_lemma")
                                printDefinitions(lemma, keywords)
            print("\n")
