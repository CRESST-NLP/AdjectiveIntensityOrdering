import numpy as np
import csv
import operator

def preference_matrix(ranks):
    """Assume that ranks are m x c, where m is the number of voters and c is the number of candidates.
    Return a matrix of size c x c.
    The value of the array [i][j] is the total count of voters who prefer candidate i over candidate j
    """
    c = len(ranks[0])
    prefs = np.zeros((c, c))

    for i in range(c):
        for j in range(c):
            for row in ranks:
                if row[i] < row[j]:
                    # voter prefers candidate i to candidate j
                    prefs[i][j] += 1
    return prefs

def prefs_string_to_ranks(string):
    """Converts preference string ABC to array of ranks {'A': 1, 'B': 2, 'C': 3}
    Ranks are 1 based
    """
    ranks = {}
    for index, value in enumerate(string):
        ranks[value] = index + 1
    return ranks

def count_pref_format_to_array(file, header=True):
    """Converts text in format:
        count, pref
        2, AB
        1, BA
        to a numpy record array representing the ranks.
        Return (headers, array of rows)

        Assumptions: Each vote specifies preferences for all candidates
    """
    csv_reader = csv.reader(csvfile)
    row_index = 1
    rank_rows = []
    for row in csv_reader:
        if row_index == 1 and header:
            # Header row, do nothing
            pass
        else:
            (count, pref_string) = row
            count = int(count)
            pref_string = pref_string.strip()
            rank_dict = prefs_string_to_ranks(pref_string)
            # Extract the headers and values sorted alphabetically
            headers = []
            values = []
            for (header, value) in sorted(rank_dict.items()):
                headers.append(header)
                values.append(value)
            # Duplicate row for each count
            for _ in range(count):
                rank_rows.append(values)
        row_index += 1

    return headers, np.array(rank_rows)

def strongest_paths_matrix(ranks):
    """
    # Input: ranks are m x c, where m is the number of voters and c is the number of candidates.
    # Output: strongest_paths[i,j], the strength of the strongest path from candidate i to candidate j.
    """

    # prefs[i,j], the number of voters who prefer candidate i to candidate j.
    prefs = preference_matrix(ranks)

    c = len(prefs[0])
    strongest_paths = np.zeros((c, c), dtype=int)
    for i in range(c):
        for j in range(c):
            if i != j:
                if prefs[i][j] > prefs[j][i]:
                    strongest_paths[i][j] = prefs[i][j]
                else:
                    strongest_paths[i][j] = 0

    for i in range(c):
        for j in range(c):
            if i != j:
                for k in range(c):
                    if i != k and j != k:
                        strongest_paths[j, k] = max(strongest_paths[j, k], min(strongest_paths[j, i], strongest_paths[i, k]))
    return strongest_paths

def schulze_method(ranks, headers):
    strongest_paths = strongest_paths_matrix(ranks)

    c = len(strongest_paths)
    rankings = np.zeros((c, c), dtype=int)
    for i in range(c):
        for j in range(i + 1, c):
            rankings[i][j] = strongest_paths[i][j] > strongest_paths[j][i]
            rankings[j][i] = strongest_paths[i][j] <= strongest_paths[j][i]

    # Summing column wise will give us ranks, from 1 being best candidate (most voted for) to c being worst (least voted for).
    # (Summing row wise will rank inversely)
    ranking_row_sums = np.sum(rankings, axis=0)
    results = {}
    # Pairs the rank with the matching header
    for (index, value) in enumerate(ranking_row_sums):
        header = headers[index]
        results[header] = value + 1

    return results

# TODO: Turn into unit test
def wikipedia_example():
    with open('./data/wikipedia_example.csv') as csvfile:
        (headers, ranks) = count_pref_format_to_array(csvfile)
        print("Preference Matrix")
        print(preference_matrix(ranks))
        print("Strongest Paths")
        print(strongest_paths_matrix(ranks))
        print("Rankings from Schulze Method")
        print(schulze_method(ranks, headers))

if __name__ == '__main__':
    ranks = np.genfromtxt('./data/happiness_rankings.csv', dtype=int, delimiter=',', names=True, comments='#')
    headers = ranks.dtype.names

    rank_dict = schulze_method(ranks, headers)
    # Print sorted
    #print("Sorted by rank:")
    #print(sorted(rank_dict.items(), key=operator.itemgetter(1)))
    #print("Sorted alphabetically:")
    sorted_alph_ranks = sorted(rank_dict.items(), key=operator.itemgetter(0))

    print(len(rank_dict.items()))

    with open('merged.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = headers)
        writer.writeheader()
        writer.writerow(rank_dict)
    # sorted_words = []
    # sorted_ranks = []
    # for (word, rank) in sorted_alph_ranks:
    #     sorted_words.append(word)
    #     sorted_ranks.append(rank)
    #
    # for (i,w) in enumerate(sorted_words):
    #     if i != len(sorted_words) - 1:
    #         print(w, end='\t')
    #     else:
    #         print(w)
    #
    # for (i,r) in enumerate(sorted_ranks):
    #     if i != len(sorted_words) - 1:
    #         print(r, end='\t')
    #     else:
    #         print(r)
