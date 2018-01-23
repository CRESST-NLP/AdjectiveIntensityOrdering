# Schulze Method

The Schulze method is a voting system that selects a single winner using votes that express preferences.
This algorithm has been adapted to merge ranking of adjectives. 
We treat the adjective as a candidate to vote for, and each person ranking as a voter.
Instead of reporting the overall winner, we report first place, second place, etc., until all ranks are filled.

See description of algorithm on wikipedia article: [Schulze Method](https://en.wikipedia.org/wiki/Schulze_method)

## Usage
Temperature ordering merging

```
python schulze.py
Sorted by rank:
[('arctics02', 1), ('icecolds01', 2), ('stonecolds01', 3), ('frostys02', 4), ('colda01', 5), ('algids01', 6), ('bleaks03', 7), ('chilly', 8), ('frigorifics01', 9), ('crisps03', 10), ('coola01', 11), ('airconditioneds01', 12), ('aircooleds01', 13), ('heatlesss01', 14), ('unheateds01', 15), ('lukewarms01', 16), ('warma01', 17), ('warmeds01', 18), ('heateds01', 19), ('thermals03', 20), ('hottishs01', 21), ('hota01', 22), ('tropicals04', 23), ('sultrys02', 24), ('swelterings01', 25), ('torrids03', 26), ('overheateds01', 27), ('bakings01', 28), ('fierys02', 29), ('blisterings02', 30), ('sizzlings01', 31), ('scorchings01', 32), ('redhots04', 33)]
Sorted alphabetically:
['airconditioneds01', 'aircooleds01', 'algids01', 'arctics02', 'bakings01', 'bleaks03', 'blisterings02', 'chilly', 'colda01', 'coola01', 'crisps03', 'fierys02', 'frigorifics01', 'frostys02', 'heateds01', 'heatlesss01', 'hota01', 'hottishs01', 'icecolds01', 'lukewarms01', 'overheateds01', 'redhots04', 'scorchings01', 'sizzlings01', 'stonecolds01', 'sultrys02', 'swelterings01', 'thermals03', 'torrids03', 'tropicals04', 'unheateds01', 'warma01', 'warmeds01']
[12, 13, 6, 1, 28, 7, 30, 8, 5, 11, 10, 29, 9, 4, 19, 14, 22, 21, 2, 16, 27, 33, 32, 31, 3, 24, 25, 20, 26, 23, 15, 17, 18]
```
