# pokemon-cli
CLI wrapper for accessing PokeAPI

## Usage

This tool requires the modules given in requirements.txt, please run `pip3 install -r requirements.txt` before attempting to use it.

1) Look up Pokemon by name. Gives the Pokemon's name, dex number, and an alpha-sorted list of moves it can learn.

`python3 pokemon.py lookup pikachu`

2) Look up pokemon by pokedex number. Gives the Pokemon's name, dex number, and an alpha-sorted list of moves it can learn.

`python3 pokemon.py lookup 25`

3) Look up moves by type. Gives the top (up to 10) most commonly learned moves. The first entry of the list is the move of the given elemental type that the most number of Pokemon can learn.

`python3 pokemon.py move-type normal`

4) Use of optional flag for filtering by generation. *Note: the generation flag and argument must come before the action (lookup, move-type).

`python3 pokemon.py --generation yellow lookup pikachu`

`python3 pokemon.py --generation yellow move-type normal`

---

## Notes

The logging module is used for showing output to user, as well as showing debug messages. Output of moves to the user is given as a comma-separated string for ease of readibility.

None of the filtering of moves learned by Pokemon distinguishes between the various methods that Pokemon can learn moves by (level up, technical machine, egg move, etc).

---

## Next Steps/Extending Functionality

* Refactor to use more util/helper functions
* Add caching to reduce load on the API and increase speed of subsequent runs
* Unit testing
* Formatting to PEP8
* Fix docstrings
