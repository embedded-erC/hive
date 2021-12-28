class GuiPiece:

    def __init__(self, piece_info: dict) -> None:
        self._location: list = piece_info['location']
        self.z_index: int = piece_info['z-index']
        self.piece_type: str = piece_info['type']
        self.piece_color: str = piece_info['color']
        self.moves: list[list] = piece_info['moves']
        self.temp_location: list = []

    def __repr__(self):
        return f'{self.full_info}, location: {self._location}, z-index: {self.z_index},  moves: {self.moves}\n'

    @property
    def full_info(self) -> str:
        return f'{self.piece_type}_{self.piece_color}'

    @property
    def location(self) -> list:
        return self.temp_location if self.temp_location else self._location

    @property
    def base_location(self) -> list:
        return self._location


class GuiButton:

    def __init__(self, text: str, height: int, width: int, rect):
        self.text = text
        self.height = height
        self.width = width
        self.rect = rect

    @property
    def top_left(self) -> tuple:
        return self.rect[0], self.rect[1]

    @property
    def dimensions(self) -> tuple:
        return self.width, self.height
