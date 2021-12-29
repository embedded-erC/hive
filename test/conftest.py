import pytest

from src.game.model import HiveGame
from src.game.consts import Consts
from src.GUI.gui_functions import GuiFunctions
from src.records.hive_recorder import HiveRecorder
import src.game.pieces as pieces


@pytest.fixture
def gui_funcs():
    gf = GuiFunctions()
    gf.set_image_size((82, 95))
    return gf


@pytest.fixture
def empty_game_board():
    return HiveGame(None)


@pytest.fixture
def game_board_single_queen():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'queen')
    return hive


@pytest.fixture
def game_board_2_queens():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'queen')
    hive.place_piece(Consts.kWhite, (0, 2), 'queen')
    return hive


@pytest.fixture
def game_board_locked_center_piece():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'queen')
    hive.place_piece(Consts.kWhite, (0, 2), 'queen')
    hive.place_piece(Consts.kBlack, (-1, -1), 'ant')
    hive.place_piece(Consts.kBlack, (1, -1), 'spider')
    return hive


@pytest.fixture
def game_board_surrounded_beetle():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'beetle')
    hive.place_piece(Consts.kBlack, (0, 2), 'beetle')
    hive.place_piece(Consts.kBlack, (0, -2), 'queen')
    hive.place_piece(Consts.kBlack, (-1, -1), 'ant')
    hive.place_piece(Consts.kBlack, (1, -1), 'spider')
    hive.place_piece(Consts.kWhite, (-1, 1), 'beetle')
    hive.place_piece(Consts.kBlack, (1, 1), 'spider')
    hive.place_piece(Consts.kWhite, (1, 3), 'spider')
    return hive


@pytest.fixture
def game_board_surrounded_grasshopper():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'grasshopper')
    hive.place_piece(Consts.kBlack, (0, 2), 'beetle')
    hive.place_piece(Consts.kBlack, (0, 4), 'beetle')
    hive.place_piece(Consts.kBlack, (0, -2), 'queen')
    hive.place_piece(Consts.kBlack, (-1, -1), 'ant')
    hive.place_piece(Consts.kBlack, (1, -1), 'spider')
    hive.place_piece(Consts.kBlack, (-1, 1), 'ant')
    hive.place_piece(Consts.kBlack, (1, 1), 'spider')
    hive.place_piece(Consts.kWhite, (2, -2), 'spider')
    hive.place_piece(Consts.kWhite, (3, -3), 'spider')
    hive.place_piece(Consts.kBlack, (4, -4), 'ant')
    hive.place_piece(Consts.kWhite, (5, -5), 'ant')
    return hive


@pytest.fixture
def game_board_surrounded_queen():
    hive = HiveGame(None)
    hive.place_piece(Consts.kBlack, (0, 0), 'queen')
    hive.place_piece(Consts.kBlack, (0, 2), 'beetle')
    hive.place_piece(Consts.kWhite, (0, -2), 'queen')
    hive.place_piece(Consts.kBlack, (-1, -1), 'ant')
    hive.place_piece(Consts.kBlack, (1, -1), 'spider')
    hive.place_piece(Consts.kBlack, (-1, 1), 'ant')
    hive.place_piece(Consts.kBlack, (1, 1), 'spider')
    hive.place_piece(Consts.kWhite, (1, 3), 'spider')
    return hive


@pytest.fixture
def center_queen():
    queen = pieces.Queen(Consts.kBlack)
    queen.location = (0, 0)
    return queen


@pytest.fixture
def edge_queen():
    queen = pieces.Queen(Consts.kBlack)
    queen.location = (0, 2)
    return queen


@pytest.fixture
def empty_saved_game():
    game_record = HiveRecorder()
    game_record.start_recording({'test_key': 'test_value'}, 'pytest', 'unittest', time_control='10+10')
    return game_record
