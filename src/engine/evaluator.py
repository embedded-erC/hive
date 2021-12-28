from src.engine.engine_config import get_config
from src.game.consts import Consts
import src.game.functions as hive_funcs


class Evaluator:
    """
    factors considered by the board evaluator:
    1. Open hexes around the queen (0 is # and highest eval possible)
        - Slidable hexes around queen
    2. Number of pieces in play
        - Weighted by piece type
    3. Number of moves for each piece in play
        - Queen mobility highly regarded
        - bonuses for pieces next to friendly queens
    4. Number of placement locations
        - N/A if all pieces in play
        - Bonus for proximity to enemy pieces (Not implemented. Pieces in enemy territory automatically take away opponent placements)
        - Bonus for proximity to enemy queen IF there are pieces other than ants still left to play
    5. Capping chain bonuses (having one piece suppress the movements of more than 1 enemy piece)
        - Queens get the largest capping bonus
        - Spiders next-highest, then grasshoppers, then ants, then beetles as worst capping pieces
        - Direct capture (180 degree opposite side) better than elbow capture (120 degree side capture)
    6. Piece location bonuses
        - Beetles next to enemy queens
        - Ants next to enemy queens IF they are locking down the queen OR the queen is already locked down
        - Spiders next to enemy queens, esp. if they are in a locking position
        - Beetles on top of enemy queens > Beetles on top of enemy ants == Beetles on top of enemy beetles
        - Negative points for beetles on top of your own pieces, especially on a friendly queen
        - Grasshopper bonuses next to friendly queens IF grasshopper has moves that take it away from the queen
        - If piece is locked, weighed by number of pieces surrounding it (more surrounded = worse piece score)
        - Beetle distance to enemy queen
    """

    def __init__(self, config=None):
        self.config = get_config(config) if not config else config
        self.board_state: dict = {}
        self.piece_locations: set[tuple] = set()
        self.placed_pieces: dict[str] = {}
        self.unplaced_pieces: dict[str] = {}
        self.colors = [Consts.kWhite, Consts.kBlack]
        self._current_color_ix = 0
        self.reset()

    @property
    def current_color_ix(self) -> int:
        return self._current_color_ix

    @current_color_ix.setter
    def current_color_ix(self, value) -> None:
        self._current_color_ix = value

    @property
    def friendly_color(self) -> str:
        return self.colors[self.current_color_ix]

    @property
    def enemy_color(self) -> str:
        return self.colors[(self.current_color_ix + 1) % 2]

    @property
    def friendly_queen_loc(self):
        return tuple(self.placed_pieces[self.friendly_color]['queen'][0]['location']) if self.placed_pieces[self.friendly_color]['queen'] else ()

    @property
    def enemy_queen_loc(self):
        return tuple(self.placed_pieces[self.enemy_color]['queen'][0]['location']) if self.placed_pieces[self.enemy_color]['queen'] else ()

    @property
    def friendly_placed_pieces(self) -> list[dict]:
        friendly_pieces = []
        [friendly_pieces.extend(pieces) for pieces in self.placed_pieces[self.friendly_color].values()]
        return friendly_pieces

    def reset(self) -> None:
        self.current_color_ix = 0
        self.placed_pieces: dict[str] = {
            Consts.kWhite: {piece[0]: [] for piece in Consts.standard_game_pieces},
            Consts.kBlack: {piece[0]: [] for piece in Consts.standard_game_pieces}
        }
        self.unplaced_pieces: dict[str] = {
            Consts.kWhite: {piece[0]: [] for piece in Consts.standard_game_pieces},
            Consts.kBlack: {piece[0]: [] for piece in Consts.standard_game_pieces}
        }

    def _disposition_pieces(self, _board_state: dict) -> None:
        self.piece_locations = set([tuple(piece['location']) for piece in _board_state['pieces'] if piece['location']])

        [self.placed_pieces[Consts.kWhite][piece['type']].append(piece) for piece in _board_state['pieces'] if piece['location'] and piece['color'] == Consts.kWhite]
        [self.placed_pieces[Consts.kBlack][piece['type']].append(piece) for piece in _board_state['pieces'] if piece['location'] and piece['color'] == Consts.kBlack]
        [self.unplaced_pieces[Consts.kWhite][piece['type']].append(piece) for piece in _board_state['pieces'] if not piece['location'] and piece['color'] == Consts.kWhite]
        [self.unplaced_pieces[Consts.kBlack][piece['type']].append(piece) for piece in _board_state['pieces'] if not piece['location'] and piece['color'] == Consts.kBlack]

    def _get_queen_eval(self) -> float:
        tally = 0.0
        if self.placed_pieces[self.friendly_color]['queen']:
            # open hexes around queen
            open_hexes_around_queen = hive_funcs.get_surrounding_hex_indexes(self.friendly_queen_loc).difference(self.piece_locations)
            if not open_hexes_around_queen:
                # Friendly queen is surrounded. This is very bad.
                tally -= 1000
            else:
                # TODO: This should probably not be linear
                tally += len(open_hexes_around_queen) * self.config['kQueen_open_hexes']

                # slideable hexes around queen are worse`
                slideable_hexes_around_queen = hive_funcs.get_slidable_moves(self.friendly_queen_loc, self.piece_locations)
                tally -= len(slideable_hexes_around_queen) * self.config['kQueen_slidable_hexes']
        return tally

    def _get_played_pieces_eval(self) -> float:
        tally = 0.0
        tally += len(self.placed_pieces[self.friendly_color]['queen']) * self.config['kQueen_in_play_bonus']
        tally += len(self.placed_pieces[self.friendly_color]['ant']) * self.config['kAnt_in_play_bonus']
        tally += len(self.placed_pieces[self.friendly_color]['beetle']) * self.config['kBeetle_in_play_bonus']
        tally += len(self.placed_pieces[self.friendly_color]['spider']) * self.config['kSpider_in_play_bonus']
        tally += len(self.placed_pieces[self.friendly_color]['grasshopper']) * self.config['kGrasshopper_in_play_bonus']
        return tally

    def _get_movement_eval(self) -> float:
        tally = 0.0

        if self.friendly_queen_loc:
            queen_neighbor_locs = hive_funcs.get_surrounding_hex_indexes(self.friendly_queen_loc).intersection(self.piece_locations)
            queen_neighbor_with_moves = [piece for piece in self.board_state['pieces'] if tuple(piece['location']) in queen_neighbor_locs and piece['moves'] and piece['color'] == self.friendly_color]
            tally += len(queen_neighbor_with_moves) * self.config['kQueen_adjacent_friendly_moves_scalar']

        for piece_type, _ in Consts.standard_game_pieces:
            tally += sum([len(piece['moves']) for piece in self.placed_pieces[self.friendly_color][piece_type]]) * self.config['kTotal_moves_scalar']
            if piece_type == 'queen':
                tally += sum([len(piece['moves']) for piece in self.placed_pieces[self.friendly_color]['queen']]) * self.config['kQueen moves scalar']
        return tally

    def _get_placements_eval(self) -> float:
        tally = 0.0
        if sum([len(pieces) for pieces in self.unplaced_pieces[self.friendly_color].values()]) > 0:
            tally += self.config['kTotal_placements_scalar'] * len(self.board_state[f'{self.friendly_color} placements'])

            if self.enemy_queen_loc:
                enemy_queen_adjacent_hexes = hive_funcs.get_surrounding_hex_indexes(tuple(self.enemy_queen_loc))
                tally += self.config['kEnemy_queen_adjacent_bonus'] * (len([location for location in self.board_state[f'{self.friendly_color} placements'] if tuple(location) in enemy_queen_adjacent_hexes]))

        return tally

    def _get_captures_eval(self) -> float:
        return 1.0

    def _get_beetle_eval(self) -> float:
        tally = 0.0
        for buried_piece in [piece for piece in self.board_state['pieces'] if piece['z-index'] < 0]:
            top_piece = [piece for piece in self.board_state['pieces'] if piece['location'] == buried_piece['location'] and piece['z-index'] == 0][0]
            if top_piece['color'] == self.friendly_color:
                if buried_piece['color'] == self.friendly_color:
                    tally -= self.config[f'kBeetle_on_friendly_{buried_piece["type"]}_penalty']
                else:
                    tally += self.config[f'kBeetle_on_enemy_{buried_piece["type"]}_bonus']
        return tally

    def _get_queen_adjustments_eval(self) -> float:
        return 1.0

    def _get_misc_eval(self) -> float:
        return self.config['kPlayer_turn_bonus'] * (self.friendly_color == self.board_state['player turn'])

    def evaluate_board_state(self, board_state: dict) -> float:
        """ Resolve various factors into a float evaluation of board state.
        Positive for white advantage, negative for black """

        players = {Consts.kWhite: 0.0, Consts.kBlack: 0.0}
        self.reset()
        self.board_state = board_state
        self._disposition_pieces(board_state)

        for color in players:
            player_evaluation = 0.0
            player_evaluation += self._get_queen_eval()
            player_evaluation += self._get_played_pieces_eval()
            player_evaluation += self._get_movement_eval()
            player_evaluation += self._get_placements_eval()
            player_evaluation += self._get_captures_eval()
            player_evaluation += self._get_beetle_eval()
            player_evaluation += self._get_queen_adjustments_eval()
            player_evaluation += self._get_misc_eval()
            players[color] = player_evaluation
            self.current_color_ix += 1

        return players[Consts.kWhite] - players[Consts.kBlack]


if __name__ == '__main__':

    from src.game.manager import HiveGameManager
    import json
    import time

    hgm = HiveGameManager()

    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (0, 0), 'type': 'queen'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (0, 2), 'type': 'queen'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (-1, -1), 'type': 'beetle'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (-1, 5), 'type': 'beetle'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (1, -1), 'type': 'ant'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (1, 3), 'type': 'ant'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (0, -2), 'type': 'grasshopper'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (0, 4), 'type': 'grasshopper'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (2, 0), 'type': 'spider'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (2, 2), 'type': 'spider'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'black', 'location': (3, -1), 'type': 'ant'}
    })
    hgm.execute_turn({
        'place piece': {'color': 'white', 'location': (1, 1), 'type': 'ant'}
    })
    state_dict = json.loads(hgm.get_game_state())
    e = Evaluator()

    start = time.perf_counter()
    counter = 0
    for _ in range(50000):
        eval = e.evaluate_board_state(state_dict)
        e.reset()
        counter += 1
    print(f"Average execution time: {(time.perf_counter() - start) / counter}")


# Full average exec time for 50k:            0.000122218022
# No Queen average exec time for 50k:        0.0000744757
# No Placed average exec time for 50k:       0.000104654179
# No Movement average exec time for 50k:     0.00009311

