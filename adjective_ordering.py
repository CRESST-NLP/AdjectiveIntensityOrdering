#!/usr/bin/env python3
from adjective_retrieval import *

high = 3
med = 2
low = 0

intensity_adverb__map = {"extremely": high, "really": high, "very": high, "intensely": high, "exceptionally": high, "highly": high,
                         "rather": med, "quite": med,
                         "fairly": low, "pretty": low, "somewhat": low, "reasonably": low, "slightly": low, "moderately": low, "a little": low, "a bit": low}

intensity_adj_map = {"high": 1, "good": 1,
                     "low": -1, "bad": -1}

# very cold, cold, fairly cold, fairly warm, warm, very warm

def orderAdjectives(adjectives):
    return adjectives

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    for property in sys.argv[1:]:
        attributes = getSynsetsWithWordNetAttributes(property)
        print(orderAdjectives(attributes))
