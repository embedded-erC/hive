import datetime
import time


def test_header_information(empty_saved_game):
    assert empty_saved_game.game_data['game information']['Player 1'] == 'pytest'
    assert empty_saved_game.game_data['game information']['Player 2'] == 'unittest'
    assert empty_saved_game.game_data['game information']['Time control'] == '10+10'


def test_filename(empty_saved_game):
    now = datetime.datetime.today()
    assert empty_saved_game.filename == f'hive_game_pytest_VS_unittest_{now.day}{now.month}{now.year}_{now.hour}{now.minute}'


def test_saved_positions(empty_saved_game):
    assert empty_saved_game.game_data['board state list'] == [({'test_key': 'test_value'}, '0.00')]


def test_reset(empty_saved_game):
    empty_saved_game.reset()
    assert empty_saved_game.game_data['game information'] == {'Player 1': '', 'Player 2': '', 'Time control': 0, 'Result': ''}
    assert empty_saved_game.game_data['board state list'] == []
    assert empty_saved_game.previous_move_timestamp == 0.0
    assert empty_saved_game.filename == ''


def test_log_move(empty_saved_game):
    null_move = {'blank position': 'blank position'}

    empty_saved_game.log_move(null_move)
    time.sleep(0.02)
    empty_saved_game.log_move(null_move)

    board_state, move_time_seconds = empty_saved_game.game_data['board state list'][-1]
    move_time_seconds = float(move_time_seconds)

    # moves are logged as a tuple of (board_state_info, move_time_seconds)
    assert board_state == null_move
    assert 0.02 <= move_time_seconds <= 0.04


def test_log_result(empty_saved_game):
    faux_result = 'Black Resigns'
    empty_saved_game.log_result(faux_result)
    assert empty_saved_game.game_data['game information']['Result'] == faux_result


def test_save_game(empty_saved_game):
    assert empty_saved_game.save_game_to_file() is False
