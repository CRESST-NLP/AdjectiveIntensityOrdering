#!/usr/bin/env python3

import json
import sys
import bz2

from nltk.corpus import wordnet as wn
import requests

import wiktionary_dict

def getSynsetsWithWordNetAttributes(property):
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

def getSynsetsWithWordNetAttributesExtended(property):
    """
    Retrieves a property's attributes from WordNet's attributes and words similar to the attributes
    :param property: A string
    :return: An array containing the property's attributes and the attributes' similar synsets
    """
    synsets = getSynsetsWithWordNetAttributes(property)
    result = set(synsets)
    for synset in synsets:
        result.update(getSimilarSynsets(synset))
    return result


def getSynsetsWithWordNetDefinitions(property, pos='a'):
    """
    Retrieves an property's attributes from WordNet's definitions
    :param property: A string i.e. "temperature"
    :param pos: A string specifying the part of speech for the property's attributes
    :return: An array containing the words with the property in its definition
    """
    # wn.NOUN = 'n'
    # wn.VERB = 'v'
    # wn.ADJ = 'a'
    # wn.ADV = 'r'

    if pos != wn.NOUN and pos != wn.VERB and pos != wn.ADJ and pos != wn.ADV:
        print("Invalid part of speech: " + pos + ". Expected 'n', 'v', 'a', or 'r'.")

    words = set()
    for synset in list(wn.all_synsets(pos)):
        if property in synset.definition():
            words.add(synset)

    return words

# caution: following method easily maxes out free Oxford API account which restricts usage to 3,000 hits/month
def getWordsUsingOxfordDefinitions(property, pos='a'):
    """
    Retrieves a property's attributes from Oxford Dictionary's definitions
    :param property: A string i.e. "temperature"
    :param pos: A string specifying the parts of speech for the property's attributes
    :return: An array containing the words with the property in its definition
    """
    # wn.NOUN = 'n'
    # wn.VERB = 'v'
    # wn.ADJ = 'a'
    # wn.ADV = 'r'

    if pos != wn.NOUN and pos != wn.VERB and pos != wn.ADJ and pos != wn.ADV:
        print("Invalid part of speech: " + pos + ". Expected 'n', 'v', 'a', or 'r'.")

    app_id = '4763721e'
    app_key = 'c019d50f24fc6f3d53ea53d7f9f0e983'

    language = 'en'

    words = set()
    for synset in list(wn.all_synsets(pos)):
        word_id = synset.name().split('.')[0]
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()
        r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
        if r:
            try:
                definitions = r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["definitions"]
                for definition in definitions:
                    if property in definition:
                        words.add(synset)
                        break
            except KeyError:
                continue

    return words

def getOxfordDefinition(word, pos='a'):
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

    if r.status_code == 200:
        # print(r.json())
        lexicalEntries = r.json()["results"][0]["lexicalEntries"]
        for lexicalEntry in lexicalEntries:
            try:
                if lexicalEntry["lexicalCategory"] == lexicalCategory:
                    json.dumps(lexicalEntry["entries"])
                    return lexicalEntry["entries"][0]["senses"][0]["definitions"][0]
            except KeyError:
                continue

    return ""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    for property in sys.argv[1:]:
        synsets = getSynsetsWithWordNetAttributes(property)
        keywords = [property] + [synset.name().split(".")[0] for synset in synsets]

        for synset in synsets:
            word = synset.name().split(".")[0]
            print("Oxford: " + word, "-", json.dumps(getOxfordDefinition(word)))
            try:
                wiki_def = wiktionary_dict.getMostLikelyDefinition(wiki[word]["A"], keywords)
                print("Wiktionary: " + word, "-", wiki_def)
            except KeyError:
                print("Wiktionary:  ")
                continue
            similarSynsets = getSimilarSynsets(synset)
            archaism = wn.synsets("archaism")[0]
            nonArchaicSimilarSynsets = set()
            archaicSimilarSynsets = set()
            for similarSynset in similarSynsets:
                try:
                    if archaism in similarSynset.usage_domains():
                        archaicSimilarSynsets.add(similarSynset)
                    else:
                        nonArchaicSimilarSynsets.add(similarSynset)
                except:
                    continue

            print(synset)
            print("\tnon-archaic similar synsets:", nonArchaicSimilarSynsets)
            print("\tarchaic synsets:", archaicSimilarSynsets)

            for synset in nonArchaicSimilarSynsets:
                word = synset.name().split(".")[0]
                print("Oxford: " + word, "-", json.dumps(getOxfordDefinition(word)))
                try:
                    wiki_def = wiktionary_dict.getMostLikelyDefinition(wiki[word]["A"], keywords)
                    print("Wiktionary: " + word, "-",  wiki_def)
                except KeyError:
                    print("Wiktionary:  ")
                    continue
            print("\n")

        adjectivesWithPropertyInDefinition = getSynsetsWithWordNetDefinitions(property)
        nonArchaicSynsetsWithPropertyInDefinition = set()
        archaicSynsetsWithPropertyInDefinition = set()
        for adjectiveWithPropertyInDefinition in adjectivesWithPropertyInDefinition:
                try:
                    if archaism in adjectiveWithPropertyInDefinition.usage_domains():
                        archaicSynsetsWithPropertyInDefinition.add(adjectiveWithPropertyInDefinition)
                    else:
                        nonArchaicSynsetsWithPropertyInDefinition.add(adjectiveWithPropertyInDefinition)
                except:
                    continue
        print("\tnon-archaic synsets with property in definition:", nonArchaicSynsetsWithPropertyInDefinition)
        print("\tarchaic synsets with pr operty in definition:", archaicSynsetsWithPropertyInDefinition)
        for synset in nonArchaicSynsetsWithPropertyInDefinition:
            word = synset.name().split(".")[0]
            print("Oxford: " + word, "-", json.dumps(getOxfordDefinition(word)))
            try:
                wiki_def = wiktionary_dict.getMostLikelyDefinition(wiki[word]["A"], keywords)
                print("Wiktionary: " + word, "-", wiki_def)
            except KeyError:
                print("Wiktionary:  ")
                continue