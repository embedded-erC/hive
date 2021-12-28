
def test_can_piece_move(center_queen, edge_queen):
    locked_center_piece_locations = {(0, 0), (0, 2), (-1, -1), (1, -1)}
    piece_chain_locations = {(0, 2), (0, 0), (0, -2), (0, -4)}

    # Slide locked pieces cannot move
    assert center_queen.can_piece_move(locked_center_piece_locations) is False

    # Moves that would segment the hive are not allowed
    assert center_queen.can_piece_move(piece_chain_locations) is False

    # Otherwise, moves are allowed
    assert edge_queen.can_piece_move(locked_center_piece_locations) is True
    assert edge_queen.can_piece_move(piece_chain_locations) is True

    # 'Covered' pieces, by a beetle or mosquito, are also not allowed to move
    edge_queen.add_covering_piece()
    assert edge_queen.can_piece_move(locked_center_piece_locations) is False
