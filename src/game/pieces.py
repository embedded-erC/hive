""" Module containing class definitions for all game piece types """

from abc import ABC, abstractmethod
import src.game.functions as hive_funcs


class HivePiece(ABC):
    """
    Base class for hive pieces. Implements most common methods for pieces.
    """

    def __init__(self, color: str):
        self.z_index: int = 0  # 0 Indicates board level, negative numbers indicate depth of coverage by other pieces
        self.color: str = color
        self.location: tuple = ()
        self.is_slide_rule_applied: bool = True
        self.is_ontop_of_hive: bool = False  # Indicates piece is climbing on other pieces in the hive

    def __str__(self):
        return self.__class__.__name__.lower()

    def __repr__(self):
        location = self.location if self.location else "unplaced"
        return f"{self.color} {self.__str__()} at {location}"

    def is_piece_surrounded(self, board_piece_locations: set[tuple]) -> bool:
        """ determine if the queen is surrounded by pieces, ending the game """
        if self.location:
            return len(hive_funcs.get_surrounding_hex_indexes(self.location).difference(board_piece_locations)) == 0
        return False

    def can_piece_move(self, board_piece_locations: set[tuple]) -> bool:
        """
        Determine if a piece is eligible to be moved

        - Piece covered by other pieces cannot move
        - Pieces that slide when moving cannot move if they are locked in place by other pieces
        - No movement may isolate a portion of the hive
        """

        # Cannot move if covered by another piece
        if self.z_index < 0:
            return False

        # Cannot move if it is a sliding piece and it is slide locked
        if self.is_slide_rule_applied and (hive_funcs.get_slidable_moves(self.location, board_piece_locations) == set()):
            return False

        # Pieces in motion may not separate the hive into disparate pieces
        return hive_funcs.is_hive_intact(board_piece_locations.difference({self.location}))

    def update_location(self, new_location: tuple) -> None:
        self.location = new_location

    def get_surrounding_locations(self) -> set[tuple]:
        """ Return a set of all six adjacent x/y locations around the piece """
        if self.z_index < 0 and self.location:
            return set()
        return hive_funcs.get_surrounding_hex_indexes(self.location)

    def add_covering_piece(self) -> None:
        """ Another piece, such as a beetle, has moved on top of this piece """
        self.z_index -= 1

    def remove_covering_piece(self) -> None:
        """ A piece that was on top of this piece has moved away """
        self.z_index += 1

    @abstractmethod
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Unique movement method that must be implemented by each piece """
        pass


class Queen(HivePiece):
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Moves one hex in any direction """
        if self.can_piece_move(board_piece_locations):
            return hive_funcs.get_slidable_moves(self.location, board_piece_locations)
        return set()


class Ant(HivePiece):
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Moves any number of hexes along the hive, provided it can slide across the table into position """
        if self.can_piece_move(board_piece_locations):
            return hive_funcs.get_all_slidable_moves(self.location, board_piece_locations)
        return set()


class Spider(HivePiece):
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Moves by sliding exactly three hexes from it's location """
        if self.can_piece_move(board_piece_locations):
            return hive_funcs.get_all_slidable_moves(self.location, board_piece_locations, is_spider_move=True)
        return set()


class Beetle(HivePiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_slide_rule_applied = False

    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Slides one hex in any direction. May climb on hive. May dismount the hive in any direction """
        if self.is_ontop_of_hive and self.z_index >= 0:
            # Every hex is available when moving off of the hive
            return hive_funcs.get_surrounding_hex_indexes(self.location)

        if self.can_piece_move(board_piece_locations):
            open_moves = hive_funcs.get_slidable_moves(self.location, board_piece_locations)
            open_moves.update(board_piece_locations.intersection(hive_funcs.get_surrounding_hex_indexes(self.location)))
            return open_moves
        return set()


class Grasshopper(HivePiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_slide_rule_applied = False

    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Moves by hopping in straight lines over neighbors. No distance limit. No slide rule """
        hoppable_hexes = set()
        if self.can_piece_move(board_piece_locations):
            neighbor_locations = hive_funcs.get_surrounding_hex_indexes(self.location).intersection(board_piece_locations)
            vectors_to_neighbors = [hive_funcs.vector_subtract(loc, self.location) for loc in neighbor_locations]
            for vector in vectors_to_neighbors:
                search_location = hive_funcs.vector_add(self.location, vector)

                while search_location in board_piece_locations:
                    search_location = hive_funcs.vector_add(search_location, vector)
                hoppable_hexes.add(search_location)

        return hoppable_hexes


class Mosquito(HivePiece):
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Not yet implemented """
        pass


class Ladybug(HivePiece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_slide_rule_applied = False

    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Not yet implemented """
        pass


class Mealworm(HivePiece):
    def get_movement_locations(self, board_piece_locations: set[tuple]) -> set[tuple]:
        """ Not yet implemented """
        pass


piece_types = {
    'queen': Queen,
    'ant': Ant,
    'spider': Spider,
    'beetle': Beetle,
    'grasshopper': Grasshopper,
    'mosquito': Mosquito,
    'ladybug': Ladybug,
    'mealworm': Mealworm
}
