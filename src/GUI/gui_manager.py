"""
Main GUI states:

1. Start (title screen?)
    - User presses New Game. Move on to Playing
2. Playing
    - Stay here until game over
3. Game Over
    - Indicate winner.
4. Reset


Board states (only active when main game is in the 'playing' state):
0. Start turn (clear any placements, user interaction hexes, etc)
1. Placement
    - Initiated by user pressing on an unplaced piece
    - Draws placement hexes for that color
    - Clicking on one of those placement hexes puts the new piece there (need a temp piece concept).
    - Clicking on a new placement hex shows the new piece there
    - Clicking on a different unplaced piece removes temp piece and starts the state over again
2. End Turn
    1. Submit turn to the manager
    2. Check for game over
    3. Move on to Start Turn
3. Move Piece
    - Initiated by user pressing on a placed piece
    - Draws movement hexes for that color
    - Clicking on one of those movement hexes puts the new piece there
    - Leaves an 'origination' hex behind
    - Clicking on a different movement hex shifts the piece there
    - Clicking on a different piece starts the state over again
4. Cancel
    - Go back to <<Start Turn>>
5. Resign
    - Indicate game over with loser as player who resigned
    - Go to <<Game Over>>
6. Game Over
    - Tell game manager to record stats
"""
import json
from src.game.manager import HiveGameManager
from src.GUI.gui_objects import GuiPiece
from src.engine.hive_engine import BasicEngine as Engine


class GuiManager:

    # Game States:
    kInitializing = 'init'
    kStart_turn = 'start turn'
    kEnd_turn = 'end turn'
    kCancel = 'cancel'
    kGame_over = 'game over'
    kPlacing = 'placing'
    kMoving = 'moving'
    kResign = 'resign'

    movement_hexes: list[list]
    placement_hexes: list[list]
    pieces: list[GuiPiece]
    selected_piece: GuiPiece = None
    board_state: dict
    board_evaluation: float

    def __init__(self):
        self.game_manager = HiveGameManager("live_game_config")
        self.game_state = self.kStart_turn  # self.kInitializing
        self.user_hex_location = []
        self.engine = Engine()
        self.refresh_board_state()
        self.board_evaluation = 1.0

    @property
    def is_game_active(self) -> bool:
        return self.game_state in [self.kStart_turn, self.kEnd_turn, self.kCancel, self.kPlacing, self.kMoving]

    @property
    def all_played_pieces(self) -> list[GuiPiece]:
        pieces_by_z_order = [piece for piece in self.pieces if piece.location and piece is not self.selected_piece]
        pieces_by_z_order.sort(key=lambda x: x.z_index)
        if self.selected_piece and self.selected_piece.location:
            pieces_by_z_order.append(self.selected_piece)
        return pieces_by_z_order

    @property
    def pieces_in_play(self) -> list[GuiPiece]:
        return [piece for piece in self.pieces if piece.location and piece.z_index >= 0]

    @property
    def active_piece_locations(self) -> list[list]:
        return [piece.base_location for piece in self.pieces_in_play]

    @property
    def winner(self) -> str:
        if self.board_state['black wins'] and self.board_state['white wins']:
            return 'Draw!'
        else:
            for color in ['white', 'black']:
                if self.board_state[f'{color} wins']:
                    return f'{color} wins!'.title()
            return ''

    def transition_to_state(self, new_state) -> None:
        if new_state in [self.kStart_turn, self.kMoving, self.kPlacing, self.kCancel]:
            self.selected_piece = None
            self.refresh_board_state()
            self.user_hex_location = []
        if self.winner:
            new_state = self.kGame_over
        self.game_state = new_state

    def get_unplayed_pieces_of_color(self, color: str) -> list[GuiPiece]:
        return [piece for piece in self.pieces if not piece.location and piece.piece_color == color]

    def get_all_pieces(self) -> list[GuiPiece]:
        return self.pieces

    def get_movement_hexes(self) -> list[list]:
        if self.selected_piece and self.game_state == self.kMoving:
            return self.selected_piece.moves
        return []

    def get_placement_hexes(self) -> list[list]:
        if self.game_state == self.kPlacing:
            return self.board_state[f'{self.board_state["player turn"]} placements']
        return []

    def refresh_board_state(self) -> None:
        self.board_state = json.loads(self.game_manager.get_game_state())
        self.pieces = [GuiPiece(piece_info) for piece_info in self.board_state['pieces']]

        if self.board_state['player turn'] == 'black' and not self.winner and self.board_state['black turns'] > 30:
            self.engine.reset(self.board_state, 5)
            engine_move = self.engine.choose_move()
            self.board_evaluation = self.engine.best_evaluation
            self.game_manager.execute_turn(engine_move)
            self.transition_to_state(self.kStart_turn)

    def start_game(self) -> None:
        self.transition_to_state(self.kStart_turn)

    def handle_turn_end(self) -> None:
        """ There's a valid turn on the board. Submit the turn to the game manager """
        turn_dict = {}
        if self.game_state == self.kPlacing:
            turn_dict['place piece'] = {'color': self.selected_piece.piece_color,
                                        'location': self.selected_piece.temp_location,
                                        'type': self.selected_piece.piece_type}

        elif self.game_state == self.kMoving:
            turn_dict['move piece'] = {'from': self.selected_piece.base_location, 'to': self.selected_piece.location}

        self.game_manager.execute_turn(turn_dict)

    def click_game_board_element(self, location: list) -> None:
        """ Disposition the click based on state """

        if self.selected_piece and location in self.selected_piece.moves:
            self.selected_piece.temp_location = location

        elif location in self.active_piece_locations:
            self.transition_to_state(self.kMoving)
            selection = [piece for piece in self.pieces if piece.location == location and piece.z_index >= 0][0]
            self.selected_piece = selection if selection.piece_color == self.board_state['player turn'] else None

        elif self.game_state == self.kPlacing and location in self.get_placement_hexes():
            self.selected_piece.temp_location = location

        self.user_hex_location = location

    def click_unplayed_piece(self, piece_type: str, color: str) -> None:
        if color == self.board_state['player turn']:
            self.transition_to_state(self.kPlacing)
            self.selected_piece = [piece for piece in self.pieces if piece.piece_type == piece_type and piece.piece_color == self.board_state['player turn'] and not piece.location][0]

            if self.board_state[f'{color} must place queen'] and self.selected_piece.piece_type != 'queen':
                self.transition_to_state(self.kStart_turn)

    def handle_reset_button(self) -> None:
        self.game_manager.execute_turn({'reset': {}})
        self.transition_to_state(self.kStart_turn)

    def handle_cancel_button(self) -> None:
        self.transition_to_state(self.kCancel)

    def handle_end_turn_button(self) -> None:
        if self.selected_piece and self.selected_piece.temp_location:
            self.handle_turn_end()
            self.transition_to_state(self.kStart_turn)

    def get_interactable_hexes(self) -> list[list]:
        interactive_hexes = []
        if self.is_game_active:
            for piece in self.pieces:
                interactive_hexes.append(piece.location)
            interactive_hexes.extend(self.get_placement_hexes())
            interactive_hexes.extend(self.get_movement_hexes())
        return [hex_loc for hex_loc in interactive_hexes if hex_loc]
