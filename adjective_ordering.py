#!/usr/bin/env python3
from adjective_retrieval import *
import csv
import wiktionary_dict

high = 1.0
low = -1.0
A = 1.2
B = 0.8
C = 0.6
# adverbs that increases the intensity of the word
intensifiers = {"extremely": A, "really": A, "very": A, "intensely": A, "exceptionally": A, "highly": A, "totally": A,
                "absolutely": A, "completely": A}

# adverbs that decrease the intensity of the word
downtoners = {"fairly": B, "pretty": B, "somewhat": C, "reasonably": C, "slightly": C, "moderately": C, "a little": C,
              "a bit": C, "rather": C, "quite": B, "mildly": C}

adj_intensity_map = {"high": high, "good": high, "great": high,
                     "low": low, "bad": low, "not": low, "opposite": low, "little": low}

wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))


def get_score(adjective, keywords, default_score=0):
    """

    :param adjective: A string containing an adjective.
    :param keywords: An array of strings containing keywords to help find the relevant definition / word sense.
    :param default_score: A float containing the default score.
    :return: A float containing the score of the adjective calculated from its definition.
    """

    score = default_score
    try:
        definitions = wiki[adjective]["A"]
        if definitions != {'1': None}:
            definition = wiktionary_dict.get_most_likely_definition(wiki[adjective]["A"], keywords).lower()
        else:
            # No Wiktionary defintion; assign WordNet definition
            definition = get_most_likely_wordnet_definition(adjective, keywords)
    except KeyError:
        # No Wiktionary defintion; assign WordNet definition
        definition = get_most_likely_wordnet_definition(adjective, keywords)

    for adj in adj_intensity_map:
        if adj in definition:
            score += adj_intensity_map[adj]

    intensity = 0
    num_intensifiers = 0
    for intensifier in intensifiers:
        if intensifier in definition:
            intensity += intensifiers[intensifier]
            num_intensifiers += 1
    if num_intensifiers > 0:
        score *= (intensity / num_intensifiers)

    downtone = 0
    num_downtoners = 0
    for downtoner in downtoners:
        if downtoner in definition:
            downtone += downtoners[downtoner]
            num_downtoners += 1
    if num_downtoners > 0:
        score *= (downtone / num_downtoners)

    return score


def order_adjectives(adjectives, keywords, default_score=0):
    """

    :param adjectives: An array of strings containing adjectives that attributes of the same property.
    :param keywords: An array of strings for helping to find the correct word sense by looking for the keyword in the
                     adjective definitions.
    :return: An array of (string, float) pairs containing adjectives and scores in order of increasing score.

    ex: input:
            adjectives: [cold, cool, hot, warm]
            keywords: [temperature, cold, cool, hot, warm]
        output:
            [('cold', -1.0), ('cool', -0.6), ('warm', 0.6), ('hot', 1.0)]
    """
    adjective_score_pairs = []

    for adjective in adjectives:
        score = get_score(adjective, keywords, default_score)
        adjective_score_pairs.append((adjective, score))

    sorted_adj_to_score = sorted(adjective_score_pairs, key=lambda tup: tup[1])
    return sorted_adj_to_score


def order_synsets(synsets, keywords, default_score=0):
    """

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
        score = get_score(get_name(s), keywords, default_score)
        if score is not None:
            synset_score_pairs.append((s, score))

    sorted_synset_to_score = sorted(synset_score_pairs, key=lambda tup: tup[1])
    return sorted_synset_to_score


def order_adjectives_extended_with_lemma_definitions(ordered_adjectives, synsets):
    """
    Expands a list of ordered adjectives using similar words and lemmas from WordNet.
    Uses lemma definitions.

    :param ordered_adjectives: An array of (string, float) pairs containing adjectives and scores in order of
                              increasing score.
    :param synsets: An array of unordered synsets with adjectives corresponding to the adjectives in ordered_adjectives.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.

    ex: input:
            ordered_adjectives: [('cold', -1.0), ('cool', -0.6), ('warm', 0.6), ('hot', 1.0)]
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
        output:

    """
    result = []
    seen_words = set()

    keywords = []
    for synset in synsets:
        keywords.extend(get_keywords(synset))

    for (adjective, score) in ordered_adjectives:
        for synset in synsets:
            if adjective == get_name(synset):
                similar_synsets = filter_archaic_synsets(get_similar_synsets(synset))
                lemmas = get_lemmas(synset)
                for word in get_lemmas(synset):
                    seen_words.add(word)
                if lemmas is None:
                    lemmas = []
                for similar_synset in similar_synsets:
                    for word in get_lemmas(similar_synset):
                        if word in seen_words:
                            continue
                        else:
                            lemmas.append(word)
                            seen_words.add(word)
                lemmas.remove(adjective)  # don't recalculate score for synset; avoids using wrong word sense
                sorted_adjective_score_pairs = order_adjectives(lemmas, keywords, score)
                sorted_adjective_score_pairs = merge(sorted_adjective_score_pairs, (adjective, score))
                result.extend(sorted_adjective_score_pairs)
                break
    return result


def order_adjectives_extended_without_lemma_definitions(ordered_adjectives, synsets):
    """
    Expands a list of ordered adjectives using similar words and lemmas from WordNet.
    Does not lemma definitions.

    :param ordered_adjectives: An array of (string, float) pairs containing adjectives and scores in order of
                              increasing score.
    :param synsets: An array of unordered synsets with adjectives corresponding to the adjectives in ordered_adjectives.
    :return: An array of strings containing the ordered attributes of a property along with similar adjectives
             according to WordNet's similar_to property.

    ex: input:
            ordered_adjectives: [('cold', -1.0), ('cool', -0.6), ('warm', 0.6), ('hot', 1.0)]
            synsets: [Synset('cold.a.01'), Synset('cool.a.01'), Synset('hot.a.01'), Synset('warm.a.01')]
        output:
    """
    result = []
    seen_words = set()

    keywords = []
    for synset in synsets:
        keywords.extend(get_keywords(synset))

    for (adjective, score) in ordered_adjectives:
        for synset in synsets:
            if adjective == get_name(synset):
                similar_synsets = filter_archaic_synsets(get_similar_synsets(synset))
                sorted_synset_score_pairs = order_synsets(similar_synsets, keywords, score)
                sorted_synset_score_pairs = merge(sorted_synset_score_pairs, (synset, score))

                for x, y in sorted_synset_score_pairs:
                    lemmas = get_lemmas(x)
                    for lemma in lemmas:
                        if lemma in seen_words:
                            continue
                        else:
                            seen_words.add(lemma)
                            result.append((lemma, y))
                break
    return result


def merge(ordered_adjectives, adjective_score_pair):
    """
    :param ordered_adjectives: An array of (string, float) pairs containing adjectives and scores in order of
                              increasing score.
    :param adjective_score_pair: A (string, float) pair containing and adjective and score.
    :return: An array of (string, float) pairs with adjective_score_pair correctly inserted into its place.
    """
    i = 0
    while i < len(ordered_adjectives):
        if adjective_score_pair[1] > ordered_adjectives[i][1]:
            i += 1
        else:
            return ordered_adjectives[:i] + [adjective_score_pair] + ordered_adjectives[i:]
    return ordered_adjectives + [adjective_score_pair]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(0)

    with open('./data/adjective_ordering_results.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        propertyName = sys.argv[1]
        synsets_result = filter_archaic_synsets(get_attributes(propertyName))
        attributes = [get_name(synset) for synset in synsets_result]
        ordered_adjectives_result = order_adjectives(attributes, [propertyName] + attributes)

        orderedAdjectivesExtended = order_adjectives_extended_with_lemma_definitions(ordered_adjectives_result, synsets_result)
        print(len(orderedAdjectivesExtended))
        print(orderedAdjectivesExtended)
        writer.writerow(orderedAdjectivesExtended)

        orderedAdjectivesExtended2 = order_adjectives_extended_without_lemma_definitions(ordered_adjectives_result, synsets_result)
        print(len(orderedAdjectivesExtended2))
        print(orderedAdjectivesExtended2)
        writer.writerow(orderedAdjectivesExtended2)





