"""
Class to record and play back Hive games
"""
import time
import json
import datetime


class HiveRecorder:
    kRecording = 'recording'
    kPlayback = 'playback'

    def __init__(self):
        self.initial_board_state: dict = {}
        self.filename: str = ''
        self.mode: str = self.kRecording
        self.move_list: list[tuple[dict, str]] = []
        self.previous_move_timestamp = None

    def start_recording(self, board_position, player_1, player_2):
        self.previous_move_timestamp = time.perf_counter()
        self.initial_board_state = board_position
        self.filename = f'hive_game_{player_1}_VS_{player_2}_{datetime.datetime.day}{datetime.datetime.month}{datetime.datetime.year}_{datetime.datetime.hour}{datetime.datetime.minute}'

    def log_move(self, move: dict):
        move_time = (time.perf_counter() - self.previous_move_timestamp) if self.previous_move_timestamp else 0.0
        self.previous_move_timestamp = time.perf_counter()

        self.move_list.append((move, f'{move_time:0.2f}'))

    def save_move_list(self):
        with open(self.filename, 'w+') as f:
            json.dump(self.move_list, f)

