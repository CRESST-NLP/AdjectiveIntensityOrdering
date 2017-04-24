import re

import spacy

from adjective_retrieval import *
import wiktionary_dict

nlp = spacy.load("en")

high = 1.0
low = -1.0
A = 1.4
A2 = 1.2
B = 0.8
B2 = 0.6

# adverbs that increases the intensity of the word
intensifiers = {"extremely": A, "intensely": A, "exceptionally": A, "astoundingly": A, "excessively": A,
                "totally": A, "absolutely": A, "completely": A, "oppressively": A, "incredibly": A, "remarkably": A,
                "particularly": A, "unusually": A, "amazingly": A, "unbearably": A, "utterly": A, "dangerously": A,
                "extraordinarily": A, "really": A, "very": A, "highly": A}

# adverbs that decrease the intensity of the word
downtoners = {"fairly": B, "pretty": B, "quite": B, "rather": B, "moderately": B,
              "somewhat": B2, "reasonably": B2, "slightly": B2, "a little": B2, "mildly": B2, "a bit": B2,
              "pleasantly": B2}

adj_intensity_map = {"high": high, "good": high, "great": high, "higher": high, "better": high, "greater": high,
                     "low": low, "bad": low, "little": low, "lower": low, "worse": low}

wiki = wiktionary_dict.load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))


def merge_compound_nouns(sentence):
    doc = nlp(sentence)

    for np in doc.noun_chunks:
        while len(np) > 1 and np[0].dep_ != 'compound':
            np = np[1:]
        if len(np) > 1:
            # Merge the tokens
            np.merge()

    results = []
    # Put underscores between compound nouns
    for token in doc:
        text = token.text.replace(' ', '_')
        results.append(text)
    return " ".join(results)


def get_definition(adjective, keywords):
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
    return definition


def score(property_name, adjective, keywords, default_score=0):
    """

    Use ordinary least squares to order attributes (x = (A_transpose * A)**-1 * A_transpose * b)

    :param adjective: A string containing an adjective.
    :param keywords: An array of strings containing keywords to help find the relevant definition / word sense.
    :param default_score: A float containing the default score.
    :return: A float containing the score of the adjective calculated from its definition.
    """


def get_score_using_next_word(property_name, adjective, keywords, default_score=0):
    """

    Only factors in adjectives into the score that precede keywords and intensifiers and downtoners that precede
    adjectives in adj_intensity_map

    :param adjective: A string containing an adjective.
    :param keywords: An array of strings containing keywords to help find the relevant definition / word sense.
    :param default_score: A float containing the default score.
    :return: A float containing the score of the adjective calculated from its definition.
    """

    score = default_score
    # handles property_names like brightness (attributes bright and dull)
    # bright's wiktionary definition doesn't have any words that would impact the score
    synsets = wn.synsets(property_name, wn.NOUN)
    for synset in synsets:
        lemmas = synset.lemmas()
        for lemma in lemmas:
            derivationally_related_forms = lemma.derivationally_related_forms()
            if adjective in [x.name() for x in derivationally_related_forms]:
                return 1
            else:
                for derivationally_related_form in derivationally_related_forms:
                    antonyms = [s.name() for s in derivationally_related_form.antonyms()]
                    if adjective in antonyms:
                        return -1

    definition = get_definition(adjective, keywords)
    definition = re.findall(r"[\w']+", definition)

    for adj in adj_intensity_map:
        if adj in definition:
            index = definition.index(adj)
            if index + 1 < len(definition) and (
                            definition[index + 1] == property_name or definition[index + 1] in adj_intensity_map):
                score += adj_intensity_map[adj]

    intensity = 0
    num_intensifiers = 0
    for intensifier in intensifiers:
        if intensifier in definition:
            index = definition.index(intensifier)
            if index + 1 < len(definition) and (
                            definition[index + 1] in keywords or definition[index + 1] in adj_intensity_map):
                intensity += intensifiers[intensifier]
                num_intensifiers += 1
    if num_intensifiers > 0:
        score *= (intensity / num_intensifiers)

    downtone = 0
    num_downtoners = 0
    for downtoner in downtoners:
        if downtoner in definition:
            index = definition.index(downtoner)
            if index + 1 < len(definition) and definition[index + 1] in keywords:
                downtone += downtoners[downtoner]
                num_downtoners += 1
    if num_downtoners > 0:
        score *= (downtone / num_downtoners)

    return score


def get_score_with_spacy(property_name, adjective, keywords, default_score=0):
    """

    Only factors in adjectives, intensifiers, and downtoners into the score depending on the dependency parse using Spacy.

    :param adjective: A string containing an adjective.
    :param keywords: An array of strings containing keywords to help find the relevant definition / word sense.
    :param default_score: A float containing the default score.
    :return: A float containing the score of the adjective calculated from its definition.
    """

    score = default_score
    # handles property_names like brightness (attributes bright and dull)
    # bright's wiktionary definition doesn't have any words that would impact the score
    synsets = wn.synsets(property_name, wn.NOUN)
    for synset in synsets:
        lemmas = synset.lemmas()
        for lemma in lemmas:
            derivationally_related_forms = lemma.derivationally_related_forms()
            if adjective in [x.name() for x in derivationally_related_forms]:
                return 1
            else:
                for derivationally_related_form in derivationally_related_forms:
                    antonyms = [s.name() for s in derivationally_related_form.antonyms()]
                    if adjective in antonyms:
                        return -1

    definition = get_definition(adjective, keywords)

    doc = nlp(merge_compound_nouns(definition))
    for word in doc:
        if (word.tag_ == "JJ" or word.tag_ == "JJR") \
                and word.text in adj_intensity_map \
                and word.head.text == property_name in keywords:
            score += adj_intensity_map[word.text]

    intensity = 0
    num_intensifiers = 0
    downtone = 0
    num_downtoners = 0
    for word in doc:
        if word.tag_ == "RB" and (word.head.text in keywords or word.head.text in adj_intensity_map):
            if word.text in intensifiers:
                intensity += intensifiers[word.text]
                num_intensifiers += 1
            elif word.text in downtoners:
                downtone += downtoners[word.text]
                num_downtoners += 1
    if num_intensifiers > 0:
        score *= (intensity / num_intensifiers)
    if num_downtoners > 0:
        score *= (downtone / num_downtoners)

    return score


def get_score_simple(property_name, adjective, keywords, default_score=0):
    """

    :param adjective: A string containing an adjective.
    :param keywords: An array of strings containing keywords to help find the relevant definition / word sense.
    :param default_score: A float containing the default score.
    :return: A float containing the score of the adjective calculated from its definition.
    """

    # handles property_names like brightness (attributes bright and dull)
    # bright's wiktionary definition doesn't have any words that would impact the score
    synsets = wn.synsets(property_name, wn.NOUN)
    for synset in synsets:
        lemmas = synset.lemmas()
        for lemma in lemmas:
            derivationally_related_forms = lemma.derivationally_related_forms()
            if adjective in [x.name() for x in derivationally_related_forms]:
                return 1
            else:
                for derivationally_related_form in derivationally_related_forms:
                    antonyms = [s.name() for s in derivationally_related_form.antonyms()]
                    if adjective in antonyms:
                        return -1

    score = default_score

    definition = get_definition(adjective, keywords)
    definition = re.findall(r"[\w']+", definition)

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
