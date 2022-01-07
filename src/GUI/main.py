"""
Thoughts on the game GUI:

Top-down board view of a table

Static window on right side split into 2 panes, each showing an ordered set of unplaced pieces.\

Confirm turn button


"""

import os
import time
import pygame
from pygame.locals import *

from src.GUI.gui_functions import GuiFunctions
from src.GUI.gui_manager import GuiManager
from src.GUI.gui_objects import GuiButton
from src.game.consts import Consts


class HiveGUI:

    # Mouse info
    kMouse_left_down = 'left down'
    kMouse_right_down = 'right down'
    kMouse_left_up = 'left up'
    kMouse_right_up = 'right up'
    kLeft_mouse_id = 1
    kRight_mouse_id = 3

    # Board size info
    kBoard_size_px = 900
    kUnplayed_area_width_px = 400

    def __init__(self):
        self.game_state = 'init'
        self.gui_funcs = GuiFunctions()
        self.manager = GuiManager()

        # Orientation Variables
        self.x_px_scalar = 42
        self.x_unplayed_px_scalar = 90
        self.y_unplayed_px_scalar = 100
        self.y_unplayed_coord = {Consts.kBlack: 50, Consts.kWhite: (self.kBoard_size_px // 2) + 50}
        self.y_px_scalar = 71
        self.mouse_pan_offset = (0, 0)
        self.temp_drag_offset = (0, 0)
        self.drag_start = (0, 0)
        self.mouse_state = self.kMouse_left_up

        # Init pygame and load basic surfaces
        pygame.init()
        pygame.display.set_caption("Hive")
        pygame.mouse.set_visible(True)
        self.screen = pygame.display.set_mode((self.kBoard_size_px + self.kUnplayed_area_width_px, self.kBoard_size_px))

        # Sidebar where unplayed pieces are kept
        self.unplayed_area_surface = pygame.Surface((self.kUnplayed_area_width_px, self.kBoard_size_px))
        self.unplayed_area_surface.convert()
        self.unplayed_area_surface_rect = self.unplayed_area_surface.get_rect().move(self.kBoard_size_px, 0)
        self.unplayed_area_surface.fill('white')
        pygame.draw.rect(self.unplayed_area_surface, 'black', (0, 0, 10, self.kBoard_size_px))
        pygame.draw.rect(self.unplayed_area_surface, 'black', (0, self.kBoard_size_px // 2, self.kUnplayed_area_width_px, 10))

        # Main game board surfaces
        self.board_surface = pygame.Surface((self.kBoard_size_px, self.kBoard_size_px))
        self.board_surface.convert()
        self.board_surface.fill('white')
        self.end_turn_button = GuiButton('End Turn', 50, 150, pygame.Rect(500, 30, 150, 50))
        self.cancel_button = GuiButton('Cancel', 50, 150, pygame.Rect(700, 30, 150, 50))
        self.reset_button = GuiButton('Reset Game', 50, 150, pygame.Rect(10, 30, 150, 50))
        self.resign_button = GuiButton('Resign', 50, 150, pygame.Rect(10, 30, 150, 50))

        self.piece_surfaces = self.load_pieces_surfaces()
        self.unplayed_piece_surface_rects_dict = dict()

        self.placements_hex_surface = pygame.image.load(os.path.join('assets', 'placement_hex.png'))
        self.movements_hex_surface = pygame.image.load(os.path.join('assets', 'moves_hex.png'))
        self.user_hex_surface = pygame.image.load(os.path.join('assets', 'user_hex.png'))
        self.gui_funcs.set_image_size(self.placements_hex_surface.get_size())

    @property
    def xy_offset(self) -> tuple:
        return self.mouse_pan_offset[0] + self.temp_drag_offset[0] + 400, self.mouse_pan_offset[1] + self.temp_drag_offset[1] + 325

    def _write_text(self, location: tuple, text: str, color: str = 'black', font_size: int = 24) -> None:
        text_image = pygame.font.SysFont('', font_size).render(text, True, color)
        self.screen.blit(text_image, location)

    def _write_centered_text(self, location: tuple, text: str, area_dimentions: tuple, color: str = 'black', font_size: int = 24) -> None:
        text_image = pygame.font.SysFont('', font_size).render(text, True, color)
        loc_to_blit_x = location[0] + area_dimentions[0] // 2 - text_image.get_width() // 2
        loc_to_blit_y = location[1] + area_dimentions[1] // 2 - text_image.get_height() // 2
        self.screen.blit(text_image, (loc_to_blit_x, loc_to_blit_y))

    def _convert_board_index_to_px(self, hex_loc: list) -> tuple:
        blit_location_x = hex_loc[1] * self.x_px_scalar + self.xy_offset[1]
        blit_location_y = hex_loc[0] * self.y_px_scalar + self.xy_offset[0]
        return blit_location_x, blit_location_y

    def _get_unplayed_pieces_count(self, color: str) -> dict:
        pieces_to_blit = dict()
        for piece in self.manager.get_unplayed_pieces_of_color(color):
            if piece.full_info not in pieces_to_blit:
                pieces_to_blit[piece.full_info] = 1
            else:
                pieces_to_blit[piece.full_info] += 1
        return pieces_to_blit

    def load_pieces_surfaces(self) -> dict[str, pygame.Surface]:
        """ Generate surfaces with an image of every piece type used for this game """
        surfaces = dict()
        for piece in self.manager.get_all_pieces():
            surfaces[piece.full_info] = pygame.image.load(os.path.join('assets', piece.full_info + '.png'))
        return surfaces

    def handle_keys(self, key) -> None:
        if key == K_ESCAPE:
            quit()

    def handle_click_in_unplayed_area(self, click_pos) -> None:
        for piece_name, rect in self.unplayed_piece_surface_rects_dict.items():
            if self.gui_funcs.is_px_in_hex(click_pos, rect.topleft) and rect.collidepoint(click_pos):
                piece_type, _, color = piece_name.partition("_")
                self.manager.click_unplayed_piece(piece_type, color)

    def handle_left_mouse_click(self, mouse_event) -> None:
        self.mouse_state = self.kMouse_left_down

        # Click is in the unplayed panel
        if self.unplayed_area_surface_rect.collidepoint(mouse_event.pos):
            self.handle_click_in_unplayed_area(mouse_event.pos)

        # Click is on the main game board
        elif self.board_surface.get_rect().collidepoint(mouse_event.pos):
            for hex_loc in self.manager.get_interactable_hexes():
                if self.gui_funcs.is_px_in_hex(mouse_event.pos, self._convert_board_index_to_px(hex_loc)):
                    self.manager.click_game_board_element(hex_loc)
                    break

            if self.cancel_button.rect.collidepoint(mouse_event.pos):
                self.manager.handle_cancel_button()

            if self.end_turn_button.rect.collidepoint(mouse_event.pos):
                self.manager.handle_end_turn_button()

            if self.reset_button.rect.collidepoint(mouse_event.pos):
                self.manager.handle_reset_button()

    def handle_mouse_click_and_motion(self, mouse_event) -> None:
        if mouse_event.type == MOUSEBUTTONDOWN and mouse_event.button == self.kRight_mouse_id:
            self.drag_start = mouse_event.pos
            self.mouse_state = self.kMouse_right_down
            self.temp_drag_offset = (0, 0)

        elif mouse_event.type == MOUSEBUTTONDOWN and mouse_event.button == self.kLeft_mouse_id:
            self.handle_left_mouse_click(mouse_event)

        elif self.mouse_state == self.kMouse_right_down and mouse_event.type == MOUSEMOTION:
            self.temp_drag_offset = (mouse_event.pos[1] - self.drag_start[1]) // 2, (mouse_event.pos[0] - self.drag_start[0]) // 2

        elif mouse_event.type == MOUSEBUTTONUP:
            self.mouse_state = self.kMouse_left_up
            self.mouse_pan_offset = self.temp_drag_offset[0] + self.mouse_pan_offset[0], self.temp_drag_offset[1] + self.mouse_pan_offset[1]
            self.temp_drag_offset = (0, 0)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
            elif event.type == KEYDOWN:
                self.handle_keys(event.key)
            elif event.type in (MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP):
                self.handle_mouse_click_and_motion(event)

    def blit_possible_moves(self) -> None:
        for hex_loc in self.manager.get_movement_hexes():
            self.screen.blit(self.movements_hex_surface, self._convert_board_index_to_px(hex_loc))

    def blit_possible_placements(self) -> None:
        for hex_loc in self.manager.get_placement_hexes():
            self.screen.blit(self.placements_hex_surface, self._convert_board_index_to_px(hex_loc))

    def blit_pieces_in_play(self) -> None:
        for piece in self.manager.all_played_pieces:
            piece_image_surface = self.piece_surfaces[piece.full_info]
            self.screen.blit(piece_image_surface, self._convert_board_index_to_px(piece.location))

    def blit_unplayed_pieces(self, color: str) -> None:
        for ix, (piece_to_blit, count) in enumerate(sorted(self._get_unplayed_pieces_count(color).items())):
            blit_location_x = self.kBoard_size_px + 27 + ((ix % 4) * self.x_unplayed_px_scalar)
            blit_location_y = self.y_unplayed_coord[color] + self.y_unplayed_px_scalar * (ix // 4)
            self.screen.blit(self.piece_surfaces[piece_to_blit], (blit_location_x, blit_location_y))
            self.unplayed_piece_surface_rects_dict[piece_to_blit] = self.piece_surfaces[piece_to_blit].get_rect().move((blit_location_x, blit_location_y))
            self._write_text((blit_location_x, blit_location_y), str(count))

    def blit_user_hex(self) -> None:
        if self.manager.user_hex_location:
            self.screen.blit(self.user_hex_surface, self._convert_board_index_to_px(self.manager.user_hex_location))

    def blit_buttons(self) -> None:
        for button in [self.end_turn_button, self.cancel_button, self.reset_button]:
            pygame.draw.rect(self.board_surface, 'black', button.rect, width=2)
            self._write_centered_text(button.top_left, button.text, button.dimensions)

    def blit_strings(self) -> None:
        self._write_centered_text((self.kBoard_size_px, 0), 'Black Pieces to Play', (self.unplayed_area_surface_rect.width, 50))
        self._write_centered_text((self.kBoard_size_px, self.kBoard_size_px // 2), 'White Pieces to Play', (self.unplayed_area_surface_rect.width, 50))
        self._write_centered_text((0, 800), self.manager.winner, (self.kBoard_size_px, 100), color='black', font_size=60)

    def draw_game_elements(self) -> None:
        self.blit_pieces_in_play()
        self.unplayed_piece_surface_rects_dict.clear()
        self.blit_unplayed_pieces(Consts.kBlack)
        self.blit_unplayed_pieces(Consts.kWhite)
        self.blit_possible_placements()
        self.blit_possible_moves()
        self.blit_user_hex()
        self.blit_strings()
        self.blit_buttons()

        # TODO: FOR TESTING ENGINE ONLY:
        self._write_centered_text((0, 850), f"Engine Eval: {self.manager.board_evaluation:.2f}", (150, 50))

    def mainloop(self) -> None:
        while True:
            self.handle_events()
            self.screen.blit(self.board_surface, (0, 0))
            self.screen.blit(self.unplayed_area_surface, (self.kBoard_size_px, 0))
            self.draw_game_elements()

            pygame.display.update()
            time.sleep(0.02)


if __name__ == '__main__':
    game = HiveGUI()
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'black', 'location': (0, 0), 'type': 'queen'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'white', 'location': (0, 2), 'type': 'queen'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'black', 'location': (1, -1), 'type': 'spider'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'white', 'location': (-1, 3), 'type': 'ant'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'black', 'location': (-1, -1), 'type': 'ant'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'white', 'location': (-1, 5), 'type': 'beetle'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'black', 'location': (0, -2), 'type': 'grasshopper'}
    })
    game.manager.game_manager.execute_turn({
        'place piece': {'color': 'white', 'location': (0, 4), 'type': 'grasshopper'}
    })
    # game.manager.game_manager.execute_turn({
    #     'place piece': {'color': 'black', 'location': (2, 0), 'type': 'spider'}
    # })
    # game.manager.game_manager.execute_turn({
    #     'place piece': {'color': 'white', 'location': (2, 2), 'type': 'spider'}
    # })
    # game.manager.game_manager.execute_turn({
    #     'place piece': {'color': 'black', 'location': (3, -1), 'type': 'ant'}
    # })
    # game.manager.game_manager.execute_turn({
    #     'place piece': {'color': 'white', 'location': (1, 1), 'type': 'ant'}
    # })
    game.manager.refresh_board_state()
    game.mainloop()


