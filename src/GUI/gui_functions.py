from src.game.functions import vector_subtract


class GuiFunctions:
    hex_image_size_px: tuple
    hex_line_slope: float = 24 / 41
    y_axis_negative_space_ratio: float = 3.96
    y_axis_bound: float

    def set_image_size(self, image_size: tuple) -> None:
        """ Set the rectangle size that bounds the game's displayed hexes """
        self.hex_image_size_px = image_size
        self.y_axis_bound = image_size[1] / self.y_axis_negative_space_ratio

    def _is_in_rect_bounds(self, offset_px: tuple) -> bool:
        return 0 <= offset_px[0] <= self.hex_image_size_px[0] and 0 <= offset_px[1] <= self.hex_image_size_px[1]

    def _is_in_hex_bounds(self, point: tuple) -> bool:
        return ((((point[0] * self.hex_line_slope) + point[1]) > self.y_axis_bound) and
                (((self.hex_image_size_px[0] - point[0]) * self.hex_line_slope) + point[1] > self.y_axis_bound) and
                ((point[0] * self.hex_line_slope) + (self.hex_image_size_px[1] - point[1]) > self.y_axis_bound) and
                (((self.hex_image_size_px[0] - point[0]) * self.hex_line_slope) + (self.hex_image_size_px[1] - point[1]) > self.y_axis_bound))

    def is_px_in_hex(self, clicked_px: tuple, hex_image_origin_px: tuple) -> bool:
        """ for a given area clicked, determine if it is within the hexagonal bounds of rectangular hex image"""
        offset_click_px = vector_subtract(clicked_px, hex_image_origin_px)
        return self._is_in_rect_bounds(offset_click_px) and self._is_in_hex_bounds(offset_click_px)
