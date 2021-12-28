""" Config values for use in Hive board evaluations """
import os
import configparser


def get_config(_config_name=''):

    config = configparser.ConfigParser()
    config_name = _config_name if _config_name else "pytest_engine_config"
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, config_name))

    config.read(config_path)
    config_dict = dict()

    try:
        # How boxed in is the queen
        config_dict['kQueen_open_hexes'] = float(config['Queens']['Open hexes around queen'])
        config_dict['kQueen_slidable_hexes'] = float(config['Queens']['Slidable hexes around queen penalty'])

        # Pieces in Play
        config_dict['kQueen_in_play_bonus'] = float(config['Pieces in Play']['Queen in play'])
        config_dict['kAnt_in_play_bonus'] = float(config['Pieces in Play']['Ant in play'])
        config_dict['kBeetle_in_play_bonus'] = float(config['Pieces in Play']['Beetle in play'])
        config_dict['kSpider_in_play_bonus'] = float(config['Pieces in Play']['Spider in play'])
        config_dict['kGrasshopper_in_play_bonus'] = float(config['Pieces in Play']['Grasshopper in play'])

        # Movement
        config_dict['kTotal_moves_scalar'] = float(config['Movement']['Total moves scalar'])
        config_dict['kQueen moves scalar'] = float(config['Movement']['Queen moves scalar'])
        config_dict['kQueen_adjacent_friendly_moves_scalar'] = float(config['Movement']['Queen adjacent friendly moves scalar'])

        # Placement

        # config_dict['kEnemy_proxy_placement_bonus'] = float(config['Placements']['Enemy proximity bonus'])

        config_dict['kEnemy_queen_adjacent_bonus'] = float(config['Placements']['Enemy queen adjacent bonus'])
        config_dict['kTotal_placements_scalar'] = float(config['Placements']['Total placements scalar'])

        # Enemy Capture - Trapping enemy pieces inside the hive with your pieces on the outside of the hive
        config_dict['kQueen_capture_bonus'] = float(config['Enemy Capture']['Queen capture bonus'])
        config_dict['kSpider_capture_bonus'] = float(config['Enemy Capture']['Spider capture bonus'])
        config_dict['kGrasshopper_capture_bonus'] = float(config['Enemy Capture']['Grasshopper capture bonus'])
        config_dict['kAnt_capture_bonus'] = float(config['Enemy Capture']['Ant capture bonus'])
        config_dict['kBeetle_capture_bonus'] = float(config['Enemy Capture']['Beetle capture bonus'])
        config_dict['kdirect_locking_bonus'] = float(config['Enemy Capture']['Direct locking bonus'])
        config_dict['kElbow_locking_bonus'] = float(config['Enemy Capture']['Elbow locking bonus'])

        # Beetle on top of hive bonuses (or penalties)
        config_dict['kBeetle_on_enemy_queen_bonus'] = float(config['Beetles']['Beetle on top of enemy queen'])
        config_dict['kBeetle_on_enemy_ant_bonus'] = float(config['Beetles']['Beetle on top of enemy ant'])
        config_dict['kBeetle_on_enemy_spider_bonus'] = float(config['Beetles']['Beetle on top of enemy spider'])
        config_dict['kBeetle_on_enemy_beetle_bonus'] = float(config['Beetles']['Beetle on top of enemy beetle'])
        config_dict['kBeetle_on_enemy_grasshopper_bonus'] = float(config['Beetles']['Beetle on top of enemy grasshopper'])

        config_dict['kBeetle_on_friendly_queen_penalty'] = float(config['Beetles']['Beetle on top of friendly queen'])
        config_dict['kBeetle_on_friendly_ant_penalty'] = float(config['Beetles']['Beetle on top of friendly ant'])
        config_dict['kBeetle_on_friendly_spider_penalty'] = float(config['Beetles']['Beetle on top of friendly spider'])
        config_dict['kBeetle_on_friendly_beetle_penalty'] = float(config['Beetles']['Beetle on top of friendly beetle'])
        config_dict['kBeetle_on_friendly_grasshopper_penalty'] = float(config['Beetles']['Beetle on top of friendly grasshopper'])

        # Adjustments for pieces near queens
        config_dict['kBeetle_locking_enemy_queen'] = float(config['Queen Adjustments']['Beetle locking enemy queen'])
        config_dict['kBeetle_adjacent_enemy_queen'] = float(config['Queen Adjustments']['Beetle adjacent to enemy queen'])
        config_dict['kAnt_locking_enemy_queen'] = float(config['Queen Adjustments']['Ant locking enemy queen'])
        config_dict['kAnt_adjacent_enemy_queen'] = float(config['Queen Adjustments']['Ant adjacent to enemy queen'])
        config_dict['kSpider_locking_enemy_queen'] = float(config['Queen Adjustments']['Spider locking enemy queen'])
        config_dict['kSpider_adjacent_enemy_queen'] = float(config['Queen Adjustments']['Spider adjacent to enemy queen'])
        config_dict['kGrasshopper_locking_enemy_queen'] = float(config['Queen Adjustments']['Grasshopper locking enemy queen'])
        config_dict['kGrasshopper_adjacent_enemy_queen'] = float(config['Queen Adjustments']['Grasshopper adjacent to enemy queen'])

        config_dict['kGrasshopper_adjacent_friendly_queen_bonus'] = float(config['Queen Adjustments']['Grasshopper adjacent to friendly queen'])
        config_dict['kBeetle_dist_enemy_queen_scalar'] = float(config['Queen Adjustments']['Beetle distance to enemy queen scalar'])

        # Other adjustments
        config_dict['kPiece_surrounded_penalty'] = float(config['Misc']['Piece surrounded penalty'])
        config_dict['kPlayer_turn_bonus'] = float(config['Misc']['Turn advantage'])

    except (ValueError, KeyError) as err:
        print("Invalid Parameters! Check your Hive config settings. Aborting.")
        quit(err)

    return config_dict
