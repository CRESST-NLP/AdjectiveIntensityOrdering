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
equation_creation.py - creates the file temperature_equations.csv

## Matrix Creation
matrix_creation.py - creates the file temperature_results.csv

## Wiktionary Dict
wiktionary_dict.py

## Score
score.py
