#!/usr/bin/env python3

import csv
from collections import deque
import sys
import argparse

import numpy as np


def get_connected_equations(word_equations_dict):
    """
    Uses a bfs method to find the connected variables in the dictionary.
    :param word_equations_dict: A dictionary mapping each word to a dictionary mapping variables to their factors.
    :return:
    """
    temp_dict = dict(word_equations_dict)
    connected_word_equations_dict = {}
    queue = deque(["high_prop"])
    while queue:
        top = queue.popleft()
        try:
            connected_word_equations_dict.update({top: temp_dict[top]})
        except KeyError:
            sys.exit("high_prop is not in equations csv")
        connected_words = list(temp_dict[top].keys())
        temp_dict.pop(top)
        for word in connected_words:
            if word in temp_dict and word not in queue:
                queue.append(word)
    return connected_word_equations_dict


def create_dict_from_equations_file(equations_csv_path, include_deduced):
    """
    Creates a dictionary mapping each word to a dictionary mapping variables to their factors.
    :param equations_csv_path: A string with the path to the csv containing the equations
    :param include_deduced: If true, includes all words. Else, only includes words connected to the variable high_prop.
    :return: A dictionary mapping each word to a dictionary mapping variables to their factors.
    """
    word_equation_dict = {}  # map from word to variable to an int representing the factor
    with open(equations_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row["Word"]
            variable = row["Variable"]
            factor = row["Factor"]
            deduced = row["Deduced"]
            if deduced == "Yes" and not include_deduced:
                continue
            if word in word_equation_dict:
                word_equation_dict[word][variable] = float(factor)
            else:
                word_equation_dict[word] = {variable: float(factor)}
    return word_equation_dict


def build_matrix(equations_csv_path, variables, connected_equations_dict):
    """
    Creates a m x n matrix, where m is the number of equations in the equations csv file and n is the number of words.
    :param equations_csv_path: A string with the path to the csv containing the equations.
    :param variables: A list of the words that correspond to the matrix columns.
    :param connected_equations_dict: A dictionary mapping each word to a dictionary mapping variables to their factors.
    All the entries in this parameter are interconnected.
    :return: A m x n matrix.
    """
    size = len(variables)
    matrix = [[0] * size for i in range(size)]
    with open(equations_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row["Word"]
            variable = row["Variable"]
            factor = float(row["Factor"])
            deduced = row["Deduced"]
            if deduced != "Yes" and word in connected_equations_dict:
                matrix[variables.index(word)][variables.index(word)] += 1
                matrix[variables.index(word)][variables.index(variable)] += -1.0 * factor

        matrix[variables.index("high_prop")][variables.index("high_prop")] = 1

    return matrix


def order_adjectives(property_name, equations_csv_path, results_path, include_all):
    """
    Orders the adjectives using least squares linear regression.
    :param equations_csv_path: A string with the path to the csv containing the equations.
    :param include_all: If true, includes all words. Else, only includes words connected to the variable high_prop.
    :return: A list of (adj, score) tuples in order of ascending score.
    """
    all_word_equations_dict = create_dict_from_equations_file(equations_csv_path, True)
    connected_word_equations_dict = get_connected_equations(all_word_equations_dict)

    if include_all:
        variables = sorted(all_word_equations_dict.keys())
        equations_dict = all_word_equations_dict
    else:
        variables = sorted(connected_word_equations_dict.keys())
        equations_dict = connected_word_equations_dict

    A = build_matrix(equations_csv_path, variables, equations_dict)

    num_rows = len(A)

    b = [0] * num_rows
    b[variables.index("high_prop")] = 10
    b = np.array(b)

    # find the least squares
    x = np.round(np.linalg.lstsq(A, b)[0], 2)
    word_score_tuples = list(zip(variables, x))

    # sort the attributes
    sorted_word_score_tuples = sorted(word_score_tuples, key=lambda tup: tup[1])

    with open(results_path, 'w') as csvfile:
        A_indices = ['A' + str(i) for i in range(num_rows)]
        fieldnames = A_indices + ['x', 'b', 'results']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        variables_header = dict(zip(A_indices, variables))
        writer.writerow(variables_header)
        for i in range(num_rows):
            map = dict(zip(A_indices, A[i]))
            map.update({'x': variables[i], 'b': b[i],
                        'results': (sorted_word_score_tuples[i][0], "%.2f" % sorted_word_score_tuples[i][1])})
            print(map['results'][0], i + 1, map['results'][1], sep=",")
            writer.writerow(map)
    return sorted_word_score_tuples


if __name__ == '__main__':
    # example:
    # > python3 matrix_creation.py temperature
    # creates the file temperature_results.csv or overwrites existing file

    parser = argparse.ArgumentParser()
    parser.add_argument("input_term", help='A string containing an attribute i.e. "temperature"')
    parser.add_argument("equations_path", help="""
        Input path to the equations file.
        Expected csv header: Word,Variable,Factor,Definition,Deduced
        Output from `equation_creation.py`
        """)
    parser.add_argument("--output", help="Output path for the equations csv file. Defaults to `input_term`_results.csv", type=str)
    args = parser.parse_args()

    if args.output is None:
        output = args.input_term + "_results.csv"
    else:
        output = args.output

    ordered_adjectives = order_adjectives(args.input_term, args.equations_path, output, False)
