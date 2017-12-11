# Adjective Ordering

## Generating Definitions

`adjective_and_definition_retrieval.py` - creates the file temperature_definitions.csv
The header of this csv file is:
```
Source,Relation,Word,WordNet Definition,Wiktionary Definition,Oxford Definition
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
This script also gets the credentials for the Oxford API, if using, through environment variables.
  - `OXFORD_API_ID=eXXXXXXX`
  - `OXFORD_API_KEY=key-here`

Register for credentials here: [https://developer.oxforddictionaries.com](https://developer.oxforddictionaries.com/)

#### Example
```                
OXFORD_API_ID=eXXXXXXX OXFORD_API_KEY=key-here python adjective_and_definition_retrieval.py temperature --wiktionary '../data/2011-08-01_OntoWiktionary_EN.xml.bz2'
```

## Equation Creation
`equation_creation.py` - creates the file temperature_equations.csv
  - Make sure to run `python -m spacy download en_depent_web_md` to get the latest data from spacy.

### Usage
```
python adjective_and_definition_retrieval.py --help
	usage: adjective_and_definition_retrieval.py [-h] [--see_also]
                                             wiktionary input_term

positional arguments:
  wiktionary  Path to 2011-08-01_OntoWiktionary_EN.xml.bz2
  input_term  A string containing an attribute i.e. "temperature"

optional arguments:
  -h, --help  show this help message and exit
  --see_also  Should the definitions collected include the `see-also` wordnet
              relation?
```

#### Example
```
python adjective_and_definition_retrieval.py '../data/2011-08-01_OntoWiktionary_EN.xml.bz2' speed --see_also
```

## Matrix Creation
matrix_creation.py - creates the file temperature_results.csv

### Usage
```
python matrix_creation.py --help
usage: matrix_creation.py [-h] [--output OUTPUT] input_term equations_path

positional arguments:
  input_term       A string containing an attribute i.e. "temperature"
  equations_path   Input path to the equations file. Expected csv header:
                   Word,Variable,Factor,Definition,Deduced Output from
                   `equation_creation.py`

optional arguments:
  -h, --help       show this help message and exit
  --output OUTPUT  Output path for the equations csv file. Defaults to
                   `input_term`_equations.csv
```

#### Example
```
python matrix_creation.py temperature ./temperature_equations.csv --output temperature_results.csv
```

## Wiktionary Dict
wiktionary_dict.py

## Score
score.py
