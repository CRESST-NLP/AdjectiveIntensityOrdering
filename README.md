# Adjective Ordering

## Generating Definitions

`adjective_and_definition_retrieval.py` - creates the file temperature_definitions.csv
The header of this csv file is:
```
Source,Relation,Word,WordNet Definition,Wikitionary Definition,Oxford Definition
```

### Usage
```
python adjective_and_definition_retrieval.py --help
usage: adjective_and_definition_retrieval.py [-h] [--wiktionary WIKTIONARY]
                                             input_term

positional arguments:
  input_term            A string containing an attribute i.e. "temperature"

optional arguments:
  -h, --help            show this help message and exit
  --wiktionary WIKTIONARY
                        Path to 2011-08-01_OntoWiktionary_EN.xml.bz2
```

#### Example
```                
python adjective_and_definition_retrieval.py temperature --wiktionary '../data/2011-08-01_OntoWiktionary_EN.xml.bz2'
```

## Equation Creation
`equation_creation.py` - creates the file temperature_equations.csv
  - Make sure to run `python -m spacy download en_depent_web_md` to get the latest data from spacy.

### Usage
```
python equation_creation.py --help
usage: equation_creation.py [-h] [--output OUTPUT] input_term definitions_path

positional arguments:
 input_term        A string containing an attribute i.e. "temperature"
 definitions_path  Input path to the definitions file. Expected csv header:
                   Source,Relation,Word,WordNet Definition,Wikitionary
                   Definition,Oxford Definition

optional arguments:
 -h, --help        show this help message and exit
 --output OUTPUT   Output path for the equations csv file. Defaults to
                   `input_term`_equations.csv
```

#### Example
```
python equation_creation.py temperature ./temperature_definitions.csv --output temperature_equations.csv
```

## Matrix Creation
matrix_creation.py - creates the file temperature_results.csv

## Wiktionary Dict
wiktionary_dict.py

## Score
score.py
