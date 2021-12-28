""" Module for the core game model """
import src.game.pieces as game_pieces
from src.game.consts import Consts, get_config


class HiveGame(object):
    """ Class responsible for maintaining game board state and knowledge of the rules of Hive """

    def __init__(self, config=None):
        self.config = get_config(config) if not config else config
        self.pieces_dict: dict[str, list[game_pieces.HivePiece]] = dict()
        self.white_turn_counter: int = 0
        self.black_turn_counter: int = 0
        self.reset_game()

    @property
    def white_queen(self) -> game_pieces.HivePiece:
        return [queen for queen in self.pieces_dict['queen'] if queen.color == Consts.kWhite][0]

    @property
    def black_queen(self) -> game_pieces.HivePiece:
        return [queen for queen in self.pieces_dict['queen'] if queen.color == Consts.kBlack][0]

    @property
    def piece_locations(self) -> list[tuple]:
        """ The x/y location of every piece placed on the game board """
        return [piece.location for piece in self.pieces if piece.location]

    @property
    def is_black_wins(self) -> bool:
        return self.white_queen.is_piece_surrounded(set(self.piece_locations))

    @property
    def is_white_wins(self) -> bool:
        return self.black_queen.is_piece_surrounded(set(self.piece_locations))

    @property
    def is_white_must_place_queen(self) -> bool:
        """ Per Hive rules: The queen must be placed on or before a player's 4th turn. """
        if self.config['kIs_sandbox_mode'] is False:
            return self.white_turn_counter >= 3 and self.white_queen.location == ()
        return False

    @property
    def is_black_must_place_queen(self) -> bool:
        """ Per Hive rules: The queen must be placed on or before a player's 4th turn. """
        if self.config['kIs_sandbox_mode'] is False:
            return self.black_turn_counter >= 3 and self.black_queen.location == ()
        return False

    @property
    def pieces(self) -> list[game_pieces.HivePiece]:
        """ flatten the dict of hive pieces into a single list containing every piece, placed or not """
        all_pieces = []
        for piece_type in self.pieces_dict.values():
            [all_pieces.append(piece) for piece in piece_type]
        return all_pieces

    @property
    def player_on_turn(self) -> str:
        """ Compare each player's turn counters to see who is on turn. Black always goes first. """
        return Consts.kBlack if (self.white_turn_counter >= self.black_turn_counter) else Consts.kWhite

    def _gen_pieces(self, _game_pieces_to_play: list[tuple]) -> None:
        """
        Create the dict that the model will use to manage all game pieces.

        _game_pieces_to_play is a list of ('piece_type', # of type). The standard game layout is defined in consts.py,
        while the optional config file contains boolean flags for expansion piece types
        """
        self.pieces_dict = {piece_name[0]: [] for piece_name in _game_pieces_to_play}
        for color in (Consts.kBlack, Consts.kWhite):
            for piece, number in _game_pieces_to_play:
                for _ in range(number):
                    self.pieces_dict[piece].append(game_pieces.piece_types[piece](color))

    def _update_turn(self, color: str) -> None:
        if color == Consts.kBlack:
            self.black_turn_counter += 1
        else:
            self.white_turn_counter += 1

    def _can_player_move(self, player_color: str) -> bool:
        """ Moving is not allowed before the queen is placed. Return False if the queen doesn't have a location"""
        player_queen = [queen for queen in self.pieces_dict['queen'] if queen.color == player_color][0]
        return player_queen.location != ()

    def _get_piece_by_location(self, selected_piece_location: tuple) -> int:
        """ Search the list of pieces for a matching location and return the list index of that piece. """
        for ix, piece in enumerate(self.pieces):
            if piece.location == selected_piece_location and piece.z_index == 0:
                return ix

    def _get_open_spaces(self, color: str) -> set[tuple]:
        """ Find and return all open hexes neighboring a given color complex and that have at least 1 neighbor piece """
        open_hexes = set()
        for piece in self.pieces:
            if piece.color == color and piece.location:
                open_hexes.update(piece.get_surrounding_locations())
        return open_hexes.difference(self.piece_locations)

    def _cover_and_uncover_pieces(self, vacated_location: tuple, newly_occupied_location: tuple, moving_piece: game_pieces.HivePiece) -> None:
        """
        Remove a 'covering' piece for all pieces on the start hex, and add one for all pieces on the ending hex

        Note: The order of moving_piece.is_ontop_of_hive flags is important. If any piece is uncovered we assume the
        moving piece has moved off of the hive. Next we see if any piece(s) have been newly covered, which places the
        moving piece back on top of the hive. Reversing this order would leave the moving piece always off of the hive
        """
        if [piece.remove_covering_piece() for piece in self.pieces if piece.location == vacated_location]:
            moving_piece.is_ontop_of_hive = False
        if [piece.add_covering_piece() for piece in self.pieces if piece.location == newly_occupied_location and piece is not moving_piece]:
            moving_piece.is_ontop_of_hive = True

    def is_player_must_pass(self, color: str) -> bool:
        """
        Determine if a player has a legal move

        A player has no legal moves if:
        1. No placed piece for that player has a valid move AND
        2. There are no placement locations available for that color OR there are no unplaced pieces
        """
        pass

    def get_piece_placement_locations(self, placement_color: str) -> set[tuple]:
        """
        Determine which hexes on the board are eligible for placement of new pieces of a given color

        There are two special cases:
        1. There are no pieces in play. It is therefore black's first turn and placement must be at location (0, 0)
        2. It is white's first turn. This is the only time placement locations are based off of the opponent's pieces
        """
        if placement_color == Consts.kBlack:
            # Show 0, 0 as the only available hex if no moves have yet been played
            return self._get_open_spaces(Consts.kBlack).difference(self._get_open_spaces(Consts.kWhite)) if self.black_turn_counter > 0 else {(0, 0)}

        elif placement_color == Consts.kWhite:
            if self.black_turn_counter == 1 and self.white_turn_counter == 0:
                # Special case on White turn 1: May place anywhere next to the first black piece
                return self._get_open_spaces(Consts.kBlack)
            else:
                return self._get_open_spaces(Consts.kWhite).difference(self._get_open_spaces(Consts.kBlack))

    def get_piece_movement_locations(self, selected_piece_location: tuple, z_index: int = 0) -> set[tuple]:
        """ For a piece on top of the hive at a given location, return a set of all possible movement locations """
        if selected_piece_location != () and z_index == 0:
            selected_piece = self.pieces[self._get_piece_by_location(selected_piece_location)]
            if self._can_player_move(selected_piece.color):
                return selected_piece.get_movement_locations(set(self.piece_locations))
        return set()

    def setup_board_state(self, board_state: dict) -> None:
        """
        Given a board_state from the game manager (manager.py), configure internal state to align with that game state

        This feature is intended for engine use w/ standard game only. Does NOT support expansion pieces
        """

        # Place pieces first, before setting turn counters
        self._gen_pieces(Consts.standard_game_pieces)
        buried_locations = []
        for piece in board_state['pieces']:
            self.place_piece(piece['color'], tuple(piece['location']), piece['type'], piece['z-index'])
            if piece['z-index'] < 0:
                buried_locations.append(tuple(piece['location']))

        for top_piece_location in buried_locations:
            self.pieces[self._get_piece_by_location(top_piece_location)].is_ontop_of_hive = True

        self.white_turn_counter = board_state['white turns']
        self.black_turn_counter = board_state['black turns']

    def reset_game(self) -> None:
        """ Initialize the game board with standard pieces and any selected optional pieces """
        self.white_turn_counter = 0
        self.black_turn_counter = 0

        game_pieces_to_play = Consts.standard_game_pieces
        if self.config['kIs_using_ladybug']:
            game_pieces_to_play.append(('ladybug', 1))
        if self.config['kIs_using_mosquito']:
            game_pieces_to_play.append(('mosquito', 1))
        if self.config['kIs_using_mealworm']:
            game_pieces_to_play.append(('mealworm', 1))

        self._gen_pieces(game_pieces_to_play)

    def place_piece(self, color: str, location: tuple, piece_type: str, z_index: int = 0) -> None:
        """
        Find the first unplayed piece of color and piece_type and set its location and piece type

        z-index parameter is zero for new pieces, possibly a negative value when setting up pieces from an existing
        game state via setup_board_state()
        """
        unplaced_of_type = [piece for piece in self.pieces if isinstance(piece, game_pieces.piece_types[piece_type]) and piece.color == color and not piece.location]
        if unplaced_of_type:
            unplaced_of_type[0].location = location
            unplaced_of_type[0].z_index = z_index
            self._update_turn(unplaced_of_type[0].color)

    def move_piece(self, selected_piece_location: tuple, new_location: tuple) -> None:
        """ Move a placed piece to a new location. This may (un)cover other pieces """
        piece_to_move = self.pieces[self._get_piece_by_location(selected_piece_location)]
        piece_to_move.location = new_location
        self._update_turn(piece_to_move.color)
        self._cover_and_uncover_pieces(selected_piece_location, new_location, piece_to_move)


# Example of a board state dict:
# sample_state = {'pieces': [{'type': 'queen', 'color': 'black', 'location': (0, 0), 'z-index': 0, 'moves': [(-1, 1), (-1, -1)]}, {'type': 'queen', 'color': 'white', 'location': (0, 2), 'z-index': -2, 'moves': []}, {'type': 'ant', 'color': 'black', 'location': (1, -1), 'z-index': 0, 'moves': [(2, -2), (2, 4), (4, 0), (-1, -1), (1, 5), (3, 1), (-1, 1), (3, -3), (-1, -3), (0, 6), (0, -4), (3, 3), (1, -3), (-1, 3), (4, -2), (-1, 5)]}, {'type': 'ant', 'color': 'black', 'location': (3, -1), 'z-index': 0, 'moves': [(2, -2), (2, 4), (-1, -1), (1, 5), (3, 1), (-1, 1), (-1, -3), (0, 6), (0, -4), (3, 3), (1, -3), (-1, 3), (-1, 5)]}, {'type': 'ant', 'color': 'black', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'ant', 'color': 'white', 'location': (1, 3), 'z-index': 0, 'moves': [(2, -2), (2, 4), (4, 0), (-1, -1), (1, 5), (3, 1), (-1, 1), (3, -3), (-1, -3), (0, 6), (0, -4), (3, 3), (-1, 3), (1, -3), (4, -2), (-1, 5)]}, {'type': 'ant', 'color': 'white', 'location': (1, 1), 'z-index': 0, 'moves': []}, {'type': 'ant', 'color': 'white', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'spider', 'color': 'black', 'location': (2, 0), 'z-index': 0, 'moves': []}, {'type': 'spider', 'color': 'black', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'spider', 'color': 'white', 'location': (2, 2), 'z-index': 0, 'moves': [(4, -2), (0, 6)]}, {'type': 'spider', 'color': 'white', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'beetle', 'color': 'black', 'location': (0, 2), 'z-index': -1, 'moves': []}, {'type': 'beetle', 'color': 'black', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'beetle', 'color': 'white', 'location': (0, 2), 'z-index': 0, 'moves': [(0, 4), (0, 0), (-1, 1), (1, 1), (-1, 3), (1, 3)]}, {'type': 'beetle', 'color': 'white', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'grasshopper', 'color': 'black', 'location': (0, -2), 'z-index': 0, 'moves': [(3, 1), (0, 6)]}, {'type': 'grasshopper', 'color': 'black', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'grasshopper', 'color': 'black', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'grasshopper', 'color': 'white', 'location': (0, 4), 'z-index': 0, 'moves': [(3, 1), (0, -4)]}, {'type': 'grasshopper', 'color': 'white', 'location': (), 'z-index': 0, 'moves': []}, {'type': 'grasshopper', 'color': 'white', 'location': (), 'z-index': 0, 'moves': []}], 'player turn': 'black', 'black placements': [(2, -2), (4, 0), (-1, -1), (3, -3), (-1, -3), (0, -4), (1, -3), (4, -2)], 'white placements': [(2, 4), (1, 5), (0, 6), (3, 3), (-1, 3), (-1, 5)], 'white must place queen': False, 'black must place queen': False, 'white wins': False, 'black wins': False, 'black turns': 8, 'white turns': 8}
