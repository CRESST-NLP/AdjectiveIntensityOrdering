#!/usr/bin/env python3
from adjective_retrieval import *
import wiktionary_dict

high = 1.0
low = -1.0
A = 1.2
B = 0.8
C = 0.6
# adverbs that increases the intensity of the worda
intensifiers = {"extremely": A, "really": A, "very": A, "intensely": A, "exceptionally": A, "highly": A, "totally": A,
                "absolutely": A, "completely": A}

# adverbs that decrease the intensity of the word
downtoners = {"fairly": B, "pretty": B, "somewhat": C, "reasonably": C, "slightly": C, "moderately": C, "a little": C,
              "a bit": C, "rather": C, "quite": B, "mildly": C}

adj_intensity_map = {"high": high, "good": high, "great": high,
                     "low": low, "bad": low, "not": low, "opposite": low, "little": low}

def getScore(adjective, keywords, defaultScore = 0):
    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))
    score = defaultScore

    try:
        definition = wiktionary_dict.getMostLikelyDefinition(wiki[adjective]["A"], keywords).lower()
    except KeyError:
        print("No wiktionary defintion for: ", adjective)
        return None

    for adj in adj_intensity_map:
        if adj in definition:
            score += adj_intensity_map[adj]

    intensity = 0
    numIntensifiers = 0
    for intensifier in intensifiers:
        if intensifier in definition:
            intensity += intensifiers[intensifier]
            numIntensifiers += 1
    if numIntensifiers > 0:
        score *= (intensity / numIntensifiers)

    downtone = 0
    numDowntoners = 0
    for downtoner in downtoners:
        if downtoner in definition:
            downtone += downtoners[downtoner]
            numDowntoners += 1
    if numDowntoners > 0:
        score *= (downtone / numDowntoners)

    return score

def orderAdjectives(adjectives, keywords, defaultScore = 0):
    """

    :param adjectives: An array of strings containing adjectives that attributes of the same property.
    :param keywords: An array of strings for helping to find the correct word sense by looking for the keyword in the
                     adjective definitions.
    :return: An array of (string, int) pairs containing adjectives and scores in order of increasing score.

    ex: input:
            adjectives: [cold, cool, hot, warm]
            keywords: [temperature, cold, cool, hot, warm]
        output:
            [('cold', -1.0), ('cool', -0.6), ('warm', 0.6), ('hot', 1.0)]
    """
    adjectiveToScore = {}

    for adjective in adjectives:
        score = getScore(adjective, keywords, defaultScore)
        if score != None:
            adjectiveToScore[adjective] = score

    adjectiveToScore = [(k,adjectiveToScore[k]) for k in adjectiveToScore.keys()]
    sortedAdjToScore = sorted(adjectiveToScore, key=lambda tup: tup[1])
    return sortedAdjToScore

def orderAdjectivesExtended(orderedAdjectives, synsets):
    """

    :param orderedAdjectives: An array of (string, int) pairs containing adjectives and scores in order of
                              increasing score.
    :param synsets: An array of unordered synsets with adjectives corresponding to the adjectives in orderedAdjectives.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.

    ex: input:
            orderedAdjectives: [('cold', -1.0), ('cool', -0.6), ('warm', 0.6), ('hot', 1.0)]
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
        output:

    """
    result = []
    for (adjective, score) in orderedAdjectives:
        for synset in synsets:
            if adjective == getName(synset):
                similarNonArchaicSynsets = filterArchaicSynsets(getSimilarSynsets(synset))
                similarAdjectives = [getName(similarSynset) for similarSynset in similarNonArchaicSynsets]
                adjectives = [adjective] + similarAdjectives
                sortedAdjectives = orderAdjectives(adjectives, adjectives, score)
                result += sortedAdjectives
                break
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    for property in sys.argv[1:]:
        synsets = filterArchaicSynsets(getSynsetsWithWordNetAttributes(property))
        attributes = [getName(synset) for synset in synsets]
        orderedAdjectives = orderAdjectives(attributes, [property] + attributes)
        print(orderedAdjectives)
        orderedAdjectivesExtended = orderAdjectivesExtended(orderedAdjectives, synsets)
        print(orderedAdjectivesExtended)
