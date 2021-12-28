import src.game.functions as hive_funcs


def test_get_surrounding_hex_indexes():
    assert hive_funcs.get_surrounding_hex_indexes((10, 10)) == {(10, 8), (9, 9), (11, 9), (9, 11), (10, 12), (11, 11)}


def test_is_move_slide_locked():
    locked_center_piece_locations = {(0, 0), (0, 2), (-1, -1), (1, -1)}

    # Center 'piece' cannot slide anywhere
    assert hive_funcs.is_move_slide_locked((0, 0), (-1, 1), locked_center_piece_locations) is True
    assert hive_funcs.is_move_slide_locked((0, 0), (1, 1), locked_center_piece_locations) is True
    assert hive_funcs.is_move_slide_locked((0, 0), (0, -2), locked_center_piece_locations) is True

    # Edge pieces can slide
    assert hive_funcs.is_move_slide_locked((0, 2), (1, 1), locked_center_piece_locations) is False

    surrounded_empty_hex_locations = {(0, -2), (-1, -1), (1, -1), (-1, 1), (0, 2), (1, 1)}

    # Pieces cannot slide into the empty center
    assert hive_funcs.is_move_slide_locked((0, 2), (0, 0), surrounded_empty_hex_locations) is True

    # Piece can slide around the outside
    assert hive_funcs.is_move_slide_locked((0, 2), (1, 3), surrounded_empty_hex_locations) is False


def test_get_slideable_moves():
    # All 3 open spaces are slide locked
    locked_center_piece_locations = {(0, 0), (0, 2), (-1, -1), (1, -1)}
    assert hive_funcs.get_slidable_moves((0, 0), locked_center_piece_locations) == set()

    # 1 open space is slide locked
    partially_locked_piece_locations = {(0, 0), (0, 2), (0, -2), (1, -1)}
    assert hive_funcs.get_slidable_moves((0, 0), partially_locked_piece_locations) == {(-1, 1), (-1, -1)}


def test_is_hive_intact():
    tiny_hive = {(0, 0)}
    large_intact_hive = {(10, 8), (9, 9), (11, 9), (9, 11), (10, 12), (11, 11), (10, 6), (10, 4), (9, 3), (11, 3)}

    broken_hive = {(0, 0), (3, 3)}
    large_broken_hive = {(10, 8), (9, 9), (11, 9), (9, 11), (10, 12), (11, 11), (10, 4), (9, 3), (11, 3)}

    assert hive_funcs.is_hive_intact(tiny_hive) is True
    assert hive_funcs.is_hive_intact(large_intact_hive) is True

    assert hive_funcs.is_hive_intact(broken_hive) is False
    assert hive_funcs.is_hive_intact(large_broken_hive) is False


def test_get_all_slidable_moves():
    basic_hive = {(0, 0), (0, 2), (0, 4)}
    surrounded_empty_hex_locations = {(0, -2), (-1, -1), (1, -1), (-1, 1), (0, 2), (1, 1)}
    assert hive_funcs.get_all_slidable_moves((0, 0), basic_hive) == {(-1, 1), (-1, 3), (-1, 5), (0, 6), (1, 5), (1, 3), (1, 1)}
    assert hive_funcs.get_all_slidable_moves((0, 0), surrounded_empty_hex_locations) == set()
    assert hive_funcs.get_all_slidable_moves((0, 2), surrounded_empty_hex_locations) == {(-1, 3), (-2, 2), (-2, 0), (-2, -2), (-1, -3), (0, -4), (1, -3), (2, -2), (2, 0), (2, 2), (1, 3)}


def test_vector_add():
    vector1 = (2, 1)
    vector2 = (5, 5)
    assert hive_funcs.vector_add(vector1, vector2) == (7, 6)
    assert hive_funcs.vector_add(vector2, vector1) == (7, 6)
    assert hive_funcs.vector_subtract(vector1, vector2) == (-3, -4)
    assert hive_funcs.vector_subtract(vector2, vector1) == (3, 4)
