#!/usr/bin/env python3

import bz2
from lxml import etree
import sys

def load_ontology(f):
    tree = etree.parse(f)
    results = tree.xpath('/OntoWiktionary[@lang="en"]/Concept/Lexicalization')

    wiki_dict = {}
    for r in results:
        lemma = r.attrib['lemma']
        pos = r.attrib['pos']
        sense = r.attrib['id'].split(":")[-1]
        if lemma not in wiki_dict:
            wiki_dict[lemma] = {}
        if pos not in wiki_dict[lemma]:
            wiki_dict[lemma][pos] = {}
        wiki_dict[lemma][pos][sense] = r.text
    return wiki_dict

def getMostLikelyDefinition(definitions, keywords):
    """

    :param definitions: an array of strings containing definitions
    :param keywords: an array of strings
    :return: string with first definition in definitions containing a keyword or the first definition
    """
    for i in range(1, 10):
        for keyword in keywords:
            if keyword in definitions[str(i)]:
                return definitions[str(i)]
    return definitions["1"]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)

    wiki = load_ontology(bz2.open('./data/2011-08-01_OntoWiktionary_EN.xml.bz2'))

    for entry in sys.argv[1:]:
        word = entry.split(",")[0]
        pos = entry.split(",")[1]

        if pos != "N" and pos != "A" and pos != "V" and pos != "R":
            print("pos should be N, A, V, or R. Given:", pos)
        else:
            try:
                res = wiki[word][pos]["1"]
                print(word + ":", res)
            except KeyError:
                print("entry not found")
