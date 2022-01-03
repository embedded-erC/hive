"""
Module containing the class to record and play back Hive games
"""
import os.path
import time
import json
import datetime


class HiveRecorder:
    """
    Class responsible for saving or loading an ordered list of hive board positions to/from a file.
    Includes general game information in a separate header
    """

    position_list: list[tuple[dict, str]]
    game_information_header: dict
    game_data: dict[str, [dict, list]]
    filename: str
    previous_move_timestamp: float

    def __init__(self):
        self.reset()
        self.saved_games_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, os.pardir, 'saved_games'))

    def start_recording(self, start_position, player_1, player_2, time_control=0) -> None:
        """ Mark the start of a hive game by generating most header information """
        date = datetime.datetime.today()
        self.filename = f'hive_game_{player_1}_VS_{player_2}_{date.day}{date.month}{date.year}_{date.hour}{date.minute}'

        self.game_information_header['Player 1'] = player_1
        self.game_information_header['Player 2'] = player_2
        self.game_information_header['Time control'] = time_control
        self.log_move(start_position)

    def log_move(self, board_state: dict) -> None:
        """ Record the next board state, along with the time delta from receipt of the previous state """
        move_time = (time.perf_counter() - self.previous_move_timestamp) if self.previous_move_timestamp else 0.0
        self.previous_move_timestamp = time.perf_counter()
        self.position_list.append((board_state, f'{move_time:0.2f}'))

    def log_result(self, result: str) -> None:
        """ Append an end-of-game result to the header """
        self.game_information_header['Result'] = result

    def reset(self) -> None:
        """ Clear all previous data and configure the recorder for the start of a new game """
        self.position_list = []
        self.game_information_header = {'Player 1': '', 'Player 2': '', 'Time control': 0, 'Result': ''}
        self.game_data = {'game information': self.game_information_header, 'board state list': self.position_list}
        self.filename: str = ''
        self.previous_move_timestamp = 0.0

    def save_game_to_file(self) -> bool:
        """ Save header and board state list to the saved_games directory. Must have a valid result to save """

        if not os.path.exists(self.saved_games_path):
            os.mkdir(self.saved_games_path)

        if self.game_information_header['Result']:
            with open(os.path.join(self.saved_games_path, self.filename), 'w+') as f:
                json.dump(self.game_data, f)
                return True
        else:
            return False
