""" Class representing Nodes of a tree data structure """


class Node:
    latest_move: list[dict]

    def __init__(self, latest_move: dict, evaluation):
        self.latest_move = [latest_move] if latest_move else list()
        self.child_nodes = list()
        self.board_evaluation: float = evaluation

    def add_child(self, latest_move: dict, evaluation) -> None:
        self.child_nodes.append(Node(latest_move, evaluation))

    def keep_best_child(self):
        best_child = sorted(self.child_nodes, key=lambda x: x.board_evaluation)[-1]
        self.child_nodes = [best_child]

    def find_best_move(self):
        if not self.child_nodes[0].child_nodes:
            # print(f"Best is: {sorted(self.child_nodes, key=lambda x: x.board_evaluation)[-1].board_evaluation=}")
            # print(f"Best is: {sorted(self.child_nodes, key=lambda x: x.board_evaluation)[0].board_evaluation=}")
            return sorted(self.child_nodes, key=lambda x: x.board_evaluation)[0]
        else:
            if not self.latest_move:
                # This is the first parent node
                best_node = Node({}, 10000)
                best_eval = 10000
                for child in self.child_nodes:
                    child_eval = child.find_best_move().board_evaluation
                    if child_eval < best_node.board_evaluation:
                        best_node = child
                        best_eval = child_eval
                return best_node.latest_move[0], best_eval
            else:
                return sorted([child.find_best_move() for child in self.child_nodes], key=lambda x: x.board_evaluation)[0]

    def get_node(self):
        if not self.child_nodes:
            yield self, self.latest_move
        else:
            for child in self.child_nodes:
                for child_node, child_moves in child.get_node():
                    move_list = self.latest_move[:]
                    move_list.extend(child_moves)
                    yield child_node, move_list
