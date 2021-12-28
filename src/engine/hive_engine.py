

"""
pseudocode

Computer plays white

1. IF white on turn:
    for step in range(3)
        1. Generate list of all possible moves for (MOVE COLOR) -> move_list
        2. Append moves to move branches
        3. Make all possible moves in move_list
        IF step == 3:
            run eval function on final board state
    choose highest (most positive for white) final eval state
    commit to making the first move of the move list

2. Data Structure:
    Basic tree structure. Each Node in the tree has the following data:
        - A board state dict
        - A float evaluation of that board state
        - A list of child nodes

    Node methods:
        -
"""
from src.game.manager import HiveGameManager
from src.engine.evaluator import Evaluator
from src.engine.node import Node

import time


class BasicEngine:
    """ Very basic engine to flesh out concepts and interfaces. Can play a game. Cannot play well """
    search_depth: int
    node_tree: Node

    def __init__(self):
        self.evaluator = Evaluator()
        self.model_manager = HiveGameManager()
        self.starting_board_state: dict = {}
        self.best_evaluation: float = 0
        self.name: str = "KOH_alpha_v1"

    def _get_node_board_state(self, _move_list: list[dict]) -> dict:
        self.model_manager.set_board_state(self.starting_board_state)
        for move in _move_list:
            self.model_manager.execute_turn(move)
        return self.model_manager.get_raw_game_state()

    def choose_move(self):
        """ This makes this engine 'basic'. Search everything for engine's moves, only 'best' moves for opponent """

        nodes = Node({}, self.evaluator.evaluate_board_state(self.starting_board_state))

        start = time.perf_counter()
        for generation in range(5):

            for node, move_list in nodes.get_node():
                new_node_game_state = self._get_node_board_state(move_list)
                for move in self.model_manager.generate_all_possible_moves(new_node_game_state):
                    self.model_manager.set_board_state(new_node_game_state)
                    self.model_manager.execute_turn(move)
                    node.add_child(move, self.evaluator.evaluate_board_state(self.model_manager.get_raw_game_state()))

                if generation % 2:
                    node.keep_best_child()

        print(f"That took {time.perf_counter() - start} seconds")
        best_move, self.best_evaluation = nodes.find_best_move()
        return best_move

    def reset(self, new_board_state, search_depth):
        if new_board_state != self.starting_board_state:
            self.starting_board_state = new_board_state
            self.search_depth = search_depth
