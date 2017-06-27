#!/usr/bin/env python3

import csv

from equation_creation import get_csv_column


def build_matrix(adj_definitions_csv, equations_csv):
    variables = list(get_csv_column('Word', equations_csv).keys())
    # adjectives = get_csv_column('Word', adj_definitions_csv)
    variables.append("high_prop")

    num_columns = len(variables)

    matrix = [[0] * num_columns for i in range(num_columns)]

    with open(equations_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            word = row["Word"]
            variable = row["Variable"]
            factor = row["Factor"]

            matrix[variables.index(word)][variables.index(variable)] = factor

        return matrix


# def order_adjectives():
#     # create matrix A from word equations
#     words = sorted(equations.keys()) + ['HT']
#     A = get_matrix(words, word_to_equations)
#
#     words = pd.read_csv(csvfile).word.tolist()
#     print(words)
#     A = build_matrix(words, csvfile)
#     print(A)
#
#     size = len(words)
#     b = np.array([0] * (size - 1) + [10])
#
#     # find the least squares
#     x = np.round(np.linalg.lstsq(A, b)[0], 2)
#     word_score_tuples = list(zip(words, x))
#
#     # sort the attributes
#     sorted_word_score_tuples = sorted(word_score_tuples, key=lambda tup: tup[1])
#     return sorted_word_score_tuples


if __name__ == '__main__':
    equations_file = "/Users/Tan/Research/2016-2017/semantic-modeling/data/equations.csv"
    adj_definitions_file = "/Users/Tan/Research/2016-2017/semantic-modeling/data/adjective_retrieval_results.csv"
    print(build_matrix(adj_definitions_file, equations_file))
