#!/usr/bin/env python3
from adjective_retrieval import *
import wiktionary_dict

high = 1.0
low = -1.0
adv_score = 0.2

# adverbs that increases the intensity of the word
intensifiers = {"extremely", "really", "very", "intensely", "exceptionally", "highly", "totally", "absolutely",
                "completely", "quite"}

# adverbs that decrease the intensity of the word
modifiers = set(["fairly", "pretty", "somewhat", "reasonably", "slightly", "moderately", "a little", "a bit", "rather",
                 "quite", "mildly", "mild"])

adj_intensity_map = {"high": high, "good": high,
                     "low": low, "bad": low, "not": low, "opposite": low}

def orderAdjectives(adjectives, keywords):
    """

    :param adjectives: An array of strings containing adjectives that attributes of the same property.
    :param keywords: An array of strings for helping to find the correct word sense by looking for the keyword in the
                     adjective definitions.
    :return: An array of strings containing ordered adjectives.

    ex: input:
            adjectives: [cold, cool, hot, warm]
            keywords: [temperature, cold, cool, hot, warm]
        output:
            [cold, cool, warm, hot]
    """
    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    adjectiveToScore = { adjective: 0 for adjective in adjectives}

    for adjective in adjectives:
        definition = wiktionary_dict.getMostLikelyDefinition(wiki[adjective]["A"], keywords).lower()
        print(adjective, ": ", definition)

        for adj in adj_intensity_map:
            if adj in definition:
                adjectiveToScore[adjective] += adj_intensity_map[adj]

        for intensifier in intensifiers:
            if intensifier in definition:
                if adjectiveToScore[adjective] > 0:
                    adjectiveToScore[adjective] += adv_score
                else:
                    adjectiveToScore[adjective] -= adv_score

        for modifier in modifiers:
            if modifier in definition:
                if adjectiveToScore[adjective] > 0:
                    adjectiveToScore[adjective] -= adv_score
                else:
                    adjectiveToScore[adjective] += adv_score

    print(adjectiveToScore)
    adjectiveToScore = [(k,adjectiveToScore[k]) for k in adjectiveToScore.keys()]
    sortedAdjToScore = sorted(adjectiveToScore, key=lambda tup: tup[1])
    result = [k for (k, v) in sortedAdjToScore]
    return result

def orderAdjectivesExtended(orderedAdjectives, synsets):
    """

    :param orderedAdjectives: An array of strings containing ordered adjectives.
    :param synsets: An array of unordered synsets with adjectives corresponding to the adjectives in orderedAdjectives.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.

    ex: input:
            orderedAdjectives: [cold, cool, warm, hot]
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
        output:
            cold, algid, arctic, bleak, chilly, crisp, frigorific, frosty, heatless, ice-cold, shivery, stone-cold,
            unheated, cool, air-conditioned, air-cooled, warm, lukewarm, warmed, hot, baking, blistering, calefacient,
            calefactory, calorific, fervent, fiery, heatable, heated, overheated, red-hot, scorching, sizzling, sultry,
            sweltering, thermal, torrid, tropical, white
    """
    result = []
    for adjective in orderedAdjectives:
        result += [adjective]
        for synset in synsets:
            if adjective == synset.name().split(".")[0]:
                result += [similarSynset.name().split(".")[0] for similarSynset in getSimilarSynsets(synset)]
                break
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    for property in sys.argv[1:]:
        synsets = getSynsetsWithWordNetAttributes(property)
        attributes = [synset.name().split(".")[0] for synset in synsets]
        orderedAdjectives = orderAdjectives(attributes, [property] + attributes)
        print(orderedAdjectives)
        orderedAdjectivesExtended = orderAdjectivesExtended(orderedAdjectives, synsets)
        print(orderedAdjectivesExtended)
