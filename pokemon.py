import requests
import argparse
import json
import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

POKEAPI_URL_BASE = "https://pokeapi.co/api/v2/"

def lookup_pokemon(pokemon, version_group):
    """
    Looks up a Pokemon given by name or dex number, then collects the moves it can learn (in version-group if provided, in all generations if not) and returns the moves as an alpha-sorted list.
    """
    logger.debug(f"Attempting to look up {pokemon}.")
    moves_list = []
    response = requests.get(POKEAPI_URL_BASE + "pokemon/" + pokemon)
    if response.ok:
        result = response.json()
        pokemon_number = result['id']
        pokemon_name = result['name']
        # Check if Pokemon is in this version-group
        if version_group:
            response = requests.get(POKEAPI_URL_BASE + "version-group/" + version_group)
            version = None
            if response.ok:
                version = response.json()['versions'][0]['name']
            if version and not any(item['version']['name']==version for item in result['game_indices']):
                    logger.debug(f"{pokemon} is not found in version {version}.")
                    return None, None, None
        # Collect list of moves learned
        for move in result['moves']:
            if version_group and any(item['version_group']['name'] == version_group for item in move['version_group_details']):
                moves_list.append(move['move']['name'])
                logger.debug(f"Included move {move['move']['name']}.")
            elif version_group:
                logger.debug(f"Skipped move {move['move']['name']}.")
                continue
            else:
                moves_list.append(move['move']['name'])
        moves_list.sort()
        return pokemon_name, pokemon_number, moves_list
    return None, None, None

def lookup_moves_by_type(args):
    """
    Looks up moves of the given type, for the (optional) version-group, and outputs the top (up to 10) most commonly learned moves.
    """
    logging.debug(f"Attempting to look up moves of type {args.type}.")
    response = requests.get(POKEAPI_URL_BASE + "type/" + args.type)
    if response.ok:
        result = response.json()
        moves_dict = {}
        for move in result['moves']:
            if args.generation and check_move_in_version_group(move['url'], args.generation):
                moves_dict[move['name']] = 0
            elif args.generation:
                continue
            else:
                moves_dict[move['name']] = 0
        if not moves_dict and args.generation:
            logger.info(f"There are no moves of type {args.type} in generation {args.generation}.")
            return
        
        pokedex_upper_index = -1
        # Currently 898
        response = requests.get(POKEAPI_URL_BASE + "pokemon-species/")
        if response.ok:
            pokedex_upper_index = int(response.json()['count'])
        for i in range(1, pokedex_upper_index + 1):
            pokemon_name, _, moves_list = lookup_pokemon(str(i), args.generation)
            logger.debug(f"Looked up {pokemon_name} at index {i}.")
            if not moves_list:
                # Assume 'None' means no more Pokemon exist within limits of version-group
                # TODO: Check this assumption
                break
            for move in moves_list:
                if move in moves_dict.keys():
                    moves_dict[move] += 1
                    logger.debug(f"Incremented count for {move}.")
        logger.debug(f"moves_dict is\n{moves_dict}")
        sorted_moves_dict = sorted(moves_dict, key=moves_dict.get, reverse=True)
        top_moves = []
        num_moves = 10
        if len(sorted_moves_dict) <= num_moves:
            top_moves = sorted_moves_dict
        else:
            top_moves = sorted_moves_dict[:10]
        logger.info(f"The most common {len(top_moves)} moves of type {args.type} are:\n{', '.join(top_moves)}")
    else:
        logger.warning(f"{args.type} does not appear to be a valid elemental type.")

def check_move_in_version_group(move_url, version_group):
    """
    Checks if a move referenced by move_url exists in the game version-group given.
    """
    response = requests.get(move_url)
    if response.ok:
        result = response.json()
        generation = get_generation_from_version_group(version_group)
        # If response.ok then this should exist
        move_generation = int(result['generation']['url'].split('/')[-2])
        return generation is not None and move_generation <= generation
    logger.debug(f"{generation} not found for move {result['name']}.")
    return False

def get_generation_from_version_group(version_group) -> int:
    """
    Finds the numerical generation that includes the given version-group.
    """
    response = requests.get(POKEAPI_URL_BASE + "version-group/" + version_group)
    if response.ok:
        return int(response.json()['generation']['url'].split('/')[-2])
    return -1

def get_arguments():
    """
    Read in arguments/flags from command line.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--generation",
        type=str,
        help="Only show info for the version-group specified"
    )
    
    subparsers = parser.add_subparsers()
    
    parser_lookup = subparsers.add_parser('lookup', help="Look up info for a Pokemon")
    parser_lookup.add_argument('pokemon', help="Pokemon name or Pokedex number")
    parser_lookup.set_defaults(func=output_lookup_pokemon)
    
    parser_movetype = subparsers.add_parser('move-type', help="Look up moves by type")
    parser_movetype.add_argument('type', help="Desired elemental type to look up")
    parser_movetype.set_defaults(func=lookup_moves_by_type)
    
    args = parser.parse_args()
    return args

def output_lookup_pokemon(args):
    """
    Looks up a Pokemon's information and outputs it.
    """
    if args.generation and get_generation_from_version_group(args.generation) == -1:
        logger.warning(f"{args.generation} is not a valid version-group.")
        return
    pokemon_name, pokemon_number, moves_list = lookup_pokemon(args.pokemon, args.generation)
    if args.generation and not pokemon_name:
        logger.warning(f"{args.pokemon} is not a valid Pokemon name or Pokedex number in version-group {args.generation}.")
    elif not pokemon_name:
        logger.warning(f"{args.pokemon} is not a valid Pokemon name or Pokedex number.")
    elif args.generation:
        logger.info(f"{pokemon_name} has Pokedex number {pokemon_number} and learns the following moves in version-group {args.generation}:\n{', '.join(moves_list)}")
    else:
        logger.info(f"{pokemon_name} has Pokedex number {pokemon_number} and learns the following moves:\n{', '.join(moves_list)}")

if __name__ == '__main__':
    args = get_arguments()
    args.func(args)
