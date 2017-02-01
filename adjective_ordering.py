#!/usr/bin/env python3
from adjective_retrieval import *
import wiktionary_dict

high = 1.0
low = -1.0
modifier_score = 0.2

adv_intensity_map = {"extremely": high, "really": high, "very": high, "intensely": high, "exceptionally": high, "highly": high}

# adverbs that decrease the intensity of the word
modifiers = set(["fairly", "pretty", "somewhat", "reasonably", "slightly", "moderately", "a little", "a bit", "rather", "quite", "mildly", "mild"])

adj_intensity_map = {"high": high, "good": high,
                     "low": low, "bad": low, "not": low, "opposite": low}

# very cold, cold, fairly cold, fairly warm, warm, very warm

def orderAdjectives(adjectives, keywords):
    wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    adjectiveToScore = { adjective: 0 for adjective in adjectives}

    for adjective in adjectives:
        definition = wiktionary_dict.getMostLikelyDefinition(wiki[adjective]["A"], keywords)
        # print(definition)
        for adv in adv_intensity_map:
            if adv in definition:
                adjectiveToScore[adjective] += adv_intensity_map[adv]
        for adj in adj_intensity_map:
            if adj in definition:
                adjectiveToScore[adjective] += adj_intensity_map[adj]
        for modifier in modifiers:
            if modifier in definition:
                # print(adjective, modifier)
                # print(adjectiveToScore[adjective])
                if adjectiveToScore[adjective] > 0:
                    adjectiveToScore[adjective] -= modifier_score
                else:
                    adjectiveToScore[adjective] += modifier_score
                # print(adjectiveToScore[adjective])

    print(adjectiveToScore)
    adjectiveToScore = [(k,adjectiveToScore[k]) for k in adjectiveToScore.keys()]
    sortedAdjToScore = sorted(adjectiveToScore, key=lambda tup: tup[1])
    result = [k for (k, v) in sortedAdjToScore]
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    for property in sys.argv[1:]:
        attributes = [synset.name().split(".")[0] for synset in getSynsetsWithWordNetAttributes(property)]
        print(orderAdjectives(attributes, [property] + attributes))
