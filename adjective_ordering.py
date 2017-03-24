#!/usr/bin/env python3

from adjective_retrieval import *
from score import get_score_using_next_word as get_score

irrelevant_adj = ["raw", "polar", "cutting", "nipping", "snappy", "refrigerant", "refrigerating", "refrigerated",
                  "shivery", "caller", "precooled", "water-cooled", "warming", "fervent", "baking_hot", "blistery",
                  "calefacient", "calefactory", "calefactive", "calorifacient", "calorific", "heatable", "heated_up",
                  "het", "het_up", "sulfurous", "sulphurous", "sweltry", "white", "white-hot", "fervid"]


def order_synsets(property_name, synsets, keywords, default_score=0):
    """

    :param property_name: A string containing the name of the property of the attributes contained in adjectives.
    :param synsets: An array of strings containing adjective synsets that attributes of the same property.
    :param keywords: An array of strings for helping to find the correct word sense by looking for the keyword in the
                     adjective definitions.
    :return: An array of (string, float) pairs containing adjectives and scores in order of increasing score.

    ex: input:
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
            keywords: [temperature, cold, cool, hot, warm]
        output:
            [(Synset('cold.a.01'), -1.0), (Synset('cool.a.01'), 0.6), (Synset('warm.a.01'), 0.6), (Synset('hot.a.01'), 1.0)]
    """
    synset_score_pairs = []

    for s in synsets:
        score = get_score(property_name, get_name(s), keywords, default_score)
        if score is not None:
            synset_score_pairs.append((s, score))

    sorted_synset_to_score = sorted(synset_score_pairs, key=lambda tup: tup[1])
    return sorted_synset_to_score


def order_adjectives_extended_with_lemma_definitions(property_name, ordered_synsets):
    """
    Returns a list of ordered adjectives using similar words and lemmas from WordNet.
    Uses Wiktionary definition. If no wiktionary definiton exists, uses WordNet definitions.

    :param property_name: A string containing the name of the property of the words in the ordered_synsets.
    :param ordered_synsets: An array of (Synset, float) pairs, where the second item is the score in order of
            increasing score.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.
    """
    result = []
    seen_words = set()

    keywords = []
    for synset in synsets:
        keywords.extend(get_keywords(synset))

    for (synset, score) in ordered_synsets:
        adjective = get_name(synset)
        similar_synsets = filter_archaic_synsets(get_similar_synsets(synset))
        lemmas = get_lemmas(synset)
        for word in lemmas:
            seen_words.add(word)
        if lemmas is None:
            lemmas = []
        for similar_synset in similar_synsets:
            for word in get_lemmas(similar_synset):
                if word in seen_words:
                    continue
                else:
                    if word not in irrelevant_adj:
                        lemmas.append(word)
                        seen_words.add(word)
        lemmas.remove(adjective)  # don't recalculate score for synset; avoids using wrong word sense

        for lemma in lemmas:
            result.append((lemma, get_score(property_name, lemma, keywords, score)))

        result.append((adjective, score))

    return sorted(result, key=lambda tup: tup[1])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(0)

    with open('./data/adjective_ordering_results.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        property_name = sys.argv[1]
        synsets = filter_archaic_synsets(get_attributes(property_name))
        attributes = [get_name(synset) for synset in synsets]
        ordered_synsets = order_synsets(property_name, synsets, [property_name] + attributes)
        print(ordered_synsets)

        orderedAdjectivesExtended = order_adjectives_extended_with_lemma_definitions(property_name, ordered_synsets)
        print(len(orderedAdjectivesExtended))
        print(orderedAdjectivesExtended)
        writer.writerow(orderedAdjectivesExtended)





