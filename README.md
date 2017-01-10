wiktionary_dict.py
- Requires [lxml](http://lxml.de/) and python 3.
-`wiktionary_dict.py` usage:
```
./wiktionary_dict.py cold,A hot,A, warm,A
cold: Having a low temperature.
hot: Of an object, having a high temperature.
warm: Having a temperature slightly higher than usual, but still pleasant; a mild temperature.

```

adjective-retrieval.py:
- This is part 1 of the semantic modeling project. It involves retrieving all the adjectives  of an attribute.
- Ex: attribute: temperature, adjectives: hot, warm, cold, etc.

adjective_ordering.py:
- This is part 2 of the semantic modeling project. It involves ordering all the adjectives  of an attribute.
- Ex: attribute: temperature, adjective ordering: cold, warm, hot

object_placement.py:
This is part 3 of the semantic modeling project. It involves placing objects on an attribute dimension graph.
Ex: attribute: temperature, graph:
        ice
      /     \
  frozen     water
 /     \     /  |  \
 ...
 cold
