from src.game.consts import Consts


def test_get_piece_placement_locations(game_board_2_queens):
    assert game_board_2_queens.get_piece_placement_locations(Consts.kBlack) == {(-1, -1), (0, -2), (1, -1)}
    assert game_board_2_queens.get_piece_placement_locations(Consts.kWhite) == {(-1, 3), (0, 4), (1, 3)}


def test_get_open_spaces(game_board_2_queens):
    assert game_board_2_queens._get_open_spaces(Consts.kBlack) == {(-1, -1), (0, -2), (1, -1), (-1, 1), (1, 1)}
    assert game_board_2_queens._get_open_spaces(Consts.kWhite) == {(-1, 1), (1, 1), (0, 4), (1, 3), (-1, 3)}


def test_get_piece_movement_locations_queen(game_board_2_queens, game_board_locked_center_piece):
    assert game_board_2_queens.get_piece_movement_locations((0, 0)) == {(-1, 1), (1, 1)}
    assert game_board_locked_center_piece.get_piece_movement_locations((0, 0)) == set()
    assert game_board_locked_center_piece.get_piece_movement_locations((0, 2)) == {(-1, 1), (1, 1)}


def test_get_piece_movement_locations_ant(game_board_locked_center_piece):
    assert game_board_locked_center_piece.get_piece_movement_locations((-1, -1)) == {(0, -2), (1, -3), (2, -2), (2, 0), (1, 3), (0, 4), (-1, 3), (-1, 1), (1, 1)}


def test_get_piece_movement_locations_spider(game_board_locked_center_piece):
    assert game_board_locked_center_piece.get_piece_movement_locations((1, -1)) == {(0, 4), (-2, -2)}


def test_get_piece_movement_locations_beetle(game_board_surrounded_beetle):
    assert game_board_surrounded_beetle.get_piece_movement_locations((0, 0)) == {(0, 2), (0, -2), (-1, -1), (-1, 1), (1, -1), (1, 1)}
    assert game_board_surrounded_beetle.get_piece_movement_locations((0, 2)) == {(0, 0), (-1, 1), (1, 1), (-1, 3), (1, 3), (0, 4)}


def test_get_piece_movement_locations_grasshopper(game_board_surrounded_grasshopper):
    assert game_board_surrounded_grasshopper.get_piece_movement_locations((0, 0)) == {(0, 6), (2, 2), (0, -4), (-2, -2), (-2, 2), (6, -6)}


def test_game_winners(game_board_surrounded_queen):
    assert game_board_surrounded_queen.is_black_wins is False
    assert game_board_surrounded_queen.is_white_wins is True

    # Swap queen placement
    game_board_surrounded_queen.move_piece((0, 0), (0, 4))
    game_board_surrounded_queen.move_piece((0, -2), (0, 0))
    game_board_surrounded_queen.move_piece((0, 4), (0, -2))

    assert game_board_surrounded_queen.is_black_wins is True
    assert game_board_surrounded_queen.is_white_wins is False


def test_cannot_move_before_queen_placed(game_board_surrounded_beetle):
    assert game_board_surrounded_beetle.get_piece_movement_locations((1, 3)) == set()
    game_board_surrounded_beetle.place_piece(Consts.kWhite, (0, 4), 'queen')
    assert game_board_surrounded_beetle.get_piece_movement_locations((1, 3)) == {(-1, 5), (2, -2)}


def test_piece_z_ordering(game_board_surrounded_beetle):
    assert set(piece.z_index for piece in game_board_surrounded_beetle.pieces) == {0}
    assert game_board_surrounded_beetle.black_queen.z_index == 0

    # Stack two pieces
    game_board_surrounded_beetle.move_piece((0, 0), (0, -2))
    assert set(piece.z_index for piece in game_board_surrounded_beetle.pieces) == {0, -1}
    assert game_board_surrounded_beetle.black_queen.z_index == -1

    # Stack a third piece
    game_board_surrounded_beetle.move_piece((1, 1), (0, -2))
    assert set(piece.z_index for piece in game_board_surrounded_beetle.pieces) == {0, -1, -2}
    assert game_board_surrounded_beetle.black_queen.z_index == -2

    # Remove the third piece
    game_board_surrounded_beetle.move_piece((0, -2), (1, 1))
    assert set(piece.z_index for piece in game_board_surrounded_beetle.pieces) == {0, -1}
    assert game_board_surrounded_beetle.black_queen.z_index == -1

    # Remove the second stacked piece to get a flat board back
    game_board_surrounded_beetle.move_piece((0, -2), (0, 0))
    assert set(piece.z_index for piece in game_board_surrounded_beetle.pieces) == {0}
    assert game_board_surrounded_beetle.black_queen.z_index == 0


def test_turn_one_placement_locations(game_board_single_queen):
    assert game_board_single_queen.get_piece_placement_locations(Consts.kWhite) == {(0, 2), (1, 1), (1, -1), (0, -2), (-1, -1), (-1, 1)}
    game_board_single_queen.place_piece(Consts.kWhite, (0, 2), 'queen')
    assert game_board_single_queen.get_piece_placement_locations(Consts.kWhite) == {(-1, 3), (0, 4), (1, 3)}


def test_turn_zero_placement_locations(empty_game_board):
    assert empty_game_board.get_piece_placement_locations(Consts.kBlack) == {(0, 0)}
