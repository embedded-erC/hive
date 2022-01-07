""" Manager/Interface for the Hive game model """

import json
from src.game.consts import get_config, Consts
from src.game.model import HiveGame
from src.records.hive_recorder import HiveRecorder

"""
This module compiles and exposes the game model state as a dict or JSON object. It converts incoming dict or JSON game 
actions into Hive game model method calls. It interfaces with the recording/playback HiveRecorder class to track games
"""


class HiveGameManager:
    def __init__(self, config=None):
        self.config = get_config(config)
        self.game_model = HiveGame(self.config)
        self.current_game_state_dict: dict = {}
        self.recorder = HiveRecorder()

    def _append_pieces_to_state(self, _state_dict: dict) -> None:
        """ Populate a list of pieces with all necessary information to display and move each piece """
        _state_dict['pieces'] = []
        for piece in self.game_model.pieces:
            _state_dict['pieces'].append(
                {
                    'type': piece.__str__(),
                    'color': piece.color,
                    'location': piece.location,
                    'z-index': piece.z_index,
                    'moves': list(self.game_model.get_piece_movement_locations(piece.location, piece.z_index)),
                }
            )

    def get_raw_game_state(self) -> dict:
        """
        Board state definition:
        1. List of pieces:
            a. Piece contents:
                -piece type
                -piece color
                -x/y hex index (index of empty tuple () indicates unplaced)
                -z-index. Indicates piece coverage index (0 is on top of hive. -1 is covered by 1 piece, etc)
                -list of possible moves. May be an empty list
        2. Player on turn
        3. List of possible placement locations for white
        4. List of possible placement locations for black
        5. White must place queen (bool)
        6. Black must place queen (bool)
        7. White has won (bool)
        8. Black has won (bool)

        Used by the model to reconstruct state from any given state_dict:
        9. Number of black turns
        10. Number of white turns
        """

        state_dict = dict()
        self._append_pieces_to_state(state_dict)
        state_dict['player turn'] = self.game_model.player_on_turn
        state_dict['white placements'] = list(self.game_model.get_piece_placement_locations(Consts.kWhite))
        state_dict['black placements'] = list(self.game_model.get_piece_placement_locations(Consts.kBlack))
        state_dict['white must place queen'] = self.game_model.is_white_must_place_queen
        state_dict['black must place queen'] = self.game_model.is_black_must_place_queen
        state_dict['white wins'] = self.game_model.is_white_wins
        state_dict['black wins'] = self.game_model.is_black_wins
        state_dict['black turns'] = self.game_model.black_turn_counter
        state_dict['white turns'] = self.game_model.white_turn_counter
        return state_dict

    def get_game_state(self) -> str:
        return json.dumps(self.get_raw_game_state(), indent=4)

    def execute_turn(self, turn: dict[str, dict]) -> None:
        """
        Possible turn types in the game of Hive:
        1. Place a piece. Indicate piece type, color, and x/y location to place
        2. Move a piece. Indicate starting and ending x/y locations
        3. Reset game. Optional: Indicate if the game should be saved by the HiveRecorder class

        dict structure:
        { turn_type(str): { turn_details1(str): details, turn_details2(str): details ... } }
        """
        if 'place piece' in turn:
            piece_color = turn['place piece']['color']
            piece_location = tuple(turn['place piece']['location'])
            piece_type = turn['place piece']['type']
            self.game_model.place_piece(piece_color, piece_location, piece_type)
        elif 'move piece' in turn:
            from_hex = tuple(turn['move piece']['from'])
            to_hex = tuple(turn['move piece']['to'])
            self.game_model.move_piece(from_hex, to_hex)
        elif 'reset' in turn:
            self.game_model.reset_game()
            if self.config['kIs_recording_game']:
                self.recorder.start_recording(self.get_raw_game_state(), self.config['kPlayer_1'], self.config['kPlayer_2'])

    def set_board_state(self, board_state: dict) -> None:
        """ Tell the game model to load a new board state. board_state is what is packaged by get_raw_game_state() """
        self.game_model.setup_board_state(board_state)

    @staticmethod
    def generate_all_possible_moves(board_state: dict) -> list[dict]:
        """
        Given a board state as returned by get_raw_game_state(), create all possible player moves for the player on turn
        Each move appended to the possible_moves list is of the dict format expected by execute_turn()
        """
        possible_moves = []

        # Placements
        if board_state[f'{board_state["player turn"]} must place queen']:
            types_to_place = ['queen']
        else:
            types_to_place = set([piece['type'] for piece in board_state['pieces'] if not piece['location'] and piece['color'] == board_state['player turn']])
        for piece_type in types_to_place:
            for location in board_state[f'{board_state["player turn"]} placements']:
                possible_moves.append({'place piece': {'color': f'{board_state["player turn"]}', 'location': location, 'type': piece_type}})

        # Movements
        for piece in board_state['pieces']:
            for moveable_hex in piece['moves']:
                if piece['color'] == board_state['player turn']:
                    possible_moves.append({'move piece': {'from': piece['location'], 'to': moveable_hex, 'type': piece['type']}})

        return possible_moves
