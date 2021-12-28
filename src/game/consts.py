""" Constant and config values for use in Hive """
import os
import configparser


class Consts:
    kBlack: str = 'black'
    kWhite: str = 'white'

    neighboring_hex_offsets: list[tuple] = [
        (0, 2), (1, 1), (1, -1), (0, -2), (-1, -1), (-1, 1)
    ]

    # Piece names and quantity in a standard Hive game:
    standard_game_pieces = [
        ('queen', 1),
        ('ant', 3),
        ('spider', 2),
        ('beetle', 2),
        ('grasshopper', 3),
    ]


def get_config(_config_name=''):

    config = configparser.ConfigParser()
    config_name = _config_name if _config_name else "pytest_config"
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, config_name))

    config.read(config_path)
    config_dict = dict()

    try:
        # Board Display Options
        config_dict['kShow_hex_grid'] = config['Board Display'].getboolean('show hex grid')

        # Expansions
        config_dict['kIs_using_ladybug'] = config['Expansions'].getboolean('ladybug')
        config_dict['kIs_using_mosquito'] = config['Expansions'].getboolean('mosquito')
        config_dict['kIs_using_mealworm'] = config['Expansions'].getboolean('mealworm')

        # Gameplay Options
        config_dict['kTime_per_game'] = int(config['Gameplay']['time limit per game'])
        config_dict['kTime_per_move'] = int(config['Gameplay']['time limit per move'])
        config_dict['kTime_increment_per_move'] = int(config['Gameplay']['time increment per move'])
        config_dict['kIs_sandbox_mode'] = config['Gameplay'].getboolean('sandbox mode')

        # Stats
        config_dict['kIs_recording_stats'] = config['Stats'].getboolean('record stats')

    except (ValueError, KeyError) as err:
        print("Invalid Parameters! Check your Hive config settings. Aborting.")
        quit(err)

    return config_dict
