import pygame
from pygame.locals import *
import sys
from math import sin, cos


class JunctionVisualiser:
    def __init__(self):
        # Initialise Pygame
        pygame.init()
        pygame.display.set_caption('Junction Visualiser')
        self._fps = 60
        self._window_clock = pygame.time.Clock()
        self._window_width, self._window_height = 640, 720
        self.window = pygame.display.set_mode((self._window_width, self._window_height))

        # Scroll Parameters
        self._mouse_position_x = 0
        self._mouse_position_y = 0
        self._scroll_offset_x = -round(self._window_width / 2)
        self._scroll_offset_y = -round(self._window_height / 2)
        self._scroll_offset_x_old = self._scroll_offset_x
        self._scroll_offset_y_old = self._scroll_offset_y
        self._scroll = False
        self._scroll_start_position_x = 0
        self._scroll_start_position_y = 0

        # Node Parameters
        self._node_diameter = 5
        self._node_colour = (0, 0, 255)
        self._tangent_scale = 0.1

        # Path Parameters
        self._path_colour = (255, 0, 0)

    # Create a blank screen, set a center point pixel, check for events and calculate dragging
    def refresh(self):
        self.window.fill((255, 255, 255))
        self.window.set_at(self._position_offsetter(0, 0), (0, 0, 0))
        self._check_for_event()
        self._check_drag()

    # Update the display
    def update(self):
        pygame.display.flip()
        self._window_clock.tick(self._fps)

    # Calculate view drag calculations
    def _check_drag(self):
        if self._scroll:
            self._scroll_offset_x = self._scroll_start_position_x - self._mouse_position_x + self._scroll_offset_x_old
            self._scroll_offset_y = self._scroll_start_position_y - self._mouse_position_y + self._scroll_offset_y_old

    # Check for events
    def _check_for_event(self):
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                self._mouse_position_x, self._mouse_position_y = event.pos
            if event.type == MOUSEBUTTONDOWN:
                self._scroll = True
                self._scroll_start_position_x = self._mouse_position_x
                self._scroll_start_position_y = self._mouse_position_y
            if event.type == MOUSEBUTTONUP:
                self._scroll = False
                self._scroll_offset_x_old = self._scroll_offset_x
                self._scroll_offset_y_old = self._scroll_offset_y
            if event.type == QUIT:
                self._close()

    # Close window
    def _close(self):
        pygame.quit()
        sys.exit()

    # Draw nodes
    def draw_nodes(self, nodes):
        for _node in nodes:
            _center_point = self._position_offsetter(_node.x, _node.y)
            _node_tangents_x, _node_tangents_y = _node.get_tangents(200)
            _direction_point = self._position_offsetter(_node.x + round(self._tangent_scale * _node_tangents_x), _node.y + round(self._tangent_scale * _node_tangents_y))
            pygame.draw.circle(self.window, self._node_colour, _center_point, radius=self._node_diameter, width=0)
            pygame.draw.line(self.window, self._node_colour, _center_point, _direction_point, width=3)
            self._draw_text(str(_node.uid), _node.x - (self._node_diameter + 5) * sin(_node.angle), _node.y + (self._node_diameter + 5) * cos(_node.angle))

    # Draw paths
    def draw_paths(self, paths):
        for _path in paths:
            _path_length = round(_path.get_length()*1.5) # Changing iteration intervals for improved performance
            for _i in range(_path_length):
                _s = _i/_path_length
                _x = _path.x_coeff[0] + _path.x_coeff[1]*_s + _path.x_coeff[2]*(_s*_s) + _path.x_coeff[3]*(_s*_s*_s)
                _y = _path.y_coeff[0] + _path.y_coeff[1]*_s + _path.y_coeff[2]*(_s*_s) + _path.y_coeff[3]*(_s*_s*_s)
                _x = round(_x)
                _y = round(_y)
                self.window.set_at(self._position_offsetter(_x, _y), self._path_colour)
                self.window.set_at(self._position_offsetter(_x+1, _y), self._path_colour)
                self.window.set_at(self._position_offsetter(_x-1, _y), self._path_colour)
                self.window.set_at(self._position_offsetter(_x, _y+1), self._path_colour)
                self.window.set_at(self._position_offsetter(_x, _y-1), self._path_colour)
                if _i == round(_path_length / 2):
                    self._draw_text(str(_path.uid), _x + 5, _y + 5)

    # Draw text
    def _draw_text(self, text, x, y):
        _font = pygame.font.Font(pygame.font.get_default_font(), 20)
        _text = _font.render(text, False, (0, 0, 0))
        self.window.blit(_text, self._position_offsetter(x - round(_text.get_width() / 2), y))

    # Offseting graphics for dragging
    def _position_offsetter(self, x, y):
        return x - self._scroll_offset_x, y - self._scroll_offset_y

