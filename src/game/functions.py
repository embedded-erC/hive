r"""
General functions for hexagonal grid operations

Index scheme for neighbor locations, with relative offsets:
                                _____
                               /     \
                              /       \
                        ,----<   0,2   >----.
                       /      \       /      \
                      /        \_____/        \
                      \ -1,1   /     \  1,1   /
                       \      /       \      /
                        >----<   0,0   >----<
                       /      \       /      \
                      /        \_____/        \
                      \ -1,-1  /     \  1,-1  /
                       \      /       \      /
                        `----<   0,-2  >----'
                              \       /
                               \_____/
"""

from src.game.consts import Consts


def vector_add(first: tuple, second: tuple) -> tuple:
    """ 2-D simple vector addition w/o numpy overhead. Tuples must be of the same size"""
    return first[0] + second[0], first[1] + second[1]


def vector_subtract(first: tuple, second: tuple) -> tuple:
    """ 2-D simple vector subtraction w/o numpy overhead. Tuples must be of the same size"""
    return first[0] - second[0], first[1] - second[1]


def get_surrounding_hex_indexes(location: tuple) -> set[tuple]:
    """ Given a hex location, return a set of the six surrounding hex locations """
    return set((vector_add(location, offset)) for offset in Consts.neighboring_hex_offsets)


def is_move_slide_locked(start_hex: tuple, ending_hex: tuple, board_piece_locations: set[tuple]) -> bool:
    """
    A move is 'slide locked' if a piece on a physical board cannot be slid from its current hex to an adjacent, empty
    hex without having to pick up the moving piece. This function expects start_hex and ending_hex to be adjacent on a
    game board.

    For any slide movement on a game board, if start_hex and ending_hex share two neighbors, the move would not be
    physically possible without picking the piece up, and thus such a move is 'slide locked'

    :param start_hex: tuple index of a starting hex for a move
    :param ending_hex: tuple index of the ending hex move
    :param board_piece_locations: set[tuple] of all pieces on a game board
    :return: bool
    """

    starting_neighbors = get_surrounding_hex_indexes(start_hex).intersection(board_piece_locations)
    ending_neighbors = get_surrounding_hex_indexes(ending_hex).intersection(board_piece_locations)
    return len(starting_neighbors.intersection(ending_neighbors)) == 2


def get_slidable_moves(starting_hex: tuple, board_piece_locations: set[tuple]) -> set[tuple]:
    """ For a given hex, determine which open adjacent hexes may be slid to """
    slidable_moves = set()
    surrounding_hexes = get_surrounding_hex_indexes(starting_hex)
    open_adjacent_hexes = surrounding_hexes.difference(board_piece_locations)
    occupied_adjacent_hexes = surrounding_hexes.intersection(board_piece_locations)
    candidate_moves = set(hex_loc for hex_loc in open_adjacent_hexes if
                          not is_move_slide_locked(starting_hex, hex_loc, board_piece_locations))
    for move in candidate_moves:
        # Must have at least 1 neighbor after a move and share at least one neighbor after a slide
        move_occupied_adjacent_hexes = get_surrounding_hex_indexes(move).intersection(board_piece_locations)
        if len(move_occupied_adjacent_hexes.difference({starting_hex})) >= 1 and \
                len(move_occupied_adjacent_hexes.intersection(occupied_adjacent_hexes)) >= 1:
            slidable_moves.add(move)
    return slidable_moves


def get_all_slidable_moves(starting_hex: tuple, board_piece_locations: set[tuple], is_spider_move: bool = False) -> set[tuple]:
    """
    Given a starting hex location, find all hexes that may be slid to. This is relevant to the Ant and Spider pieces.
    For the ant, return the exhaustive list of all contiguous slideable moves
    For the spider, return only the 3rd step in the process, as the spider must move exactly 3 hexes along the hive
    """
    search_count = 0
    board_copy = board_piece_locations.copy()

    if starting_hex in board_copy:
        board_copy.remove(starting_hex)

    available_moves = get_slidable_moves(starting_hex, board_copy)
    slidable_moves = available_moves.copy()

    while available_moves:
        search_count += 1
        new_moves = set()
        for move in available_moves:
            new_moves.update(get_slidable_moves(move, board_copy))
        available_moves = new_moves.difference(slidable_moves)
        slidable_moves.update(available_moves)

        if is_spider_move and search_count == 2:
            return available_moves

    if starting_hex in slidable_moves:
        slidable_moves.remove(starting_hex)

    return slidable_moves


def get_valid_moves(candidate_moves: set[tuple], board_piece_locations: set[tuple]) -> set[tuple]:
    """ For a set of candidate moves, filter out any moves that would result in a broken hive of multiple clusters """

    # TODO: (Hash?) and cache known good board configurations? A lookup may be faster than topological analysis
    valid_moves = set()
    for move in candidate_moves:
        candidate_board_state = board_piece_locations.copy()
        candidate_board_state.add(move)
        if is_hive_intact(candidate_board_state):
            valid_moves.add(move)
    return valid_moves


def is_hive_intact(board_piece_locations: set[tuple]) -> bool:
    """ For a given board state, determine if every piece is part of a single hive cluster. """

    def traverse_hive(hex_loc: tuple, _visited_hexes: set[tuple], _board_piece_locations: set[tuple]) -> set[tuple]:
        unvisited_neighbors = get_surrounding_hex_indexes(hex_loc).intersection(_board_piece_locations).difference(
            _visited_hexes)
        if unvisited_neighbors:
            _visited_hexes.update(unvisited_neighbors)
            for neighbor_loc in unvisited_neighbors:
                _visited_hexes.update(traverse_hive(neighbor_loc, _visited_hexes, board_piece_locations))
        return _visited_hexes

    board_size = len(board_piece_locations)
    starting_hex_loc = board_piece_locations.pop()
    all_visited_hexes = traverse_hive(starting_hex_loc, {starting_hex_loc}, board_piece_locations)
    return len(all_visited_hexes) == board_size
