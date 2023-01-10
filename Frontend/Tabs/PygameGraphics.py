import pygame
from math import sin, cos
from PyQt5 import QtCore


class VisualPoint:
    def __init__(self, x: int, y: int, colour: tuple) -> None:
        """

        :param x: x coordinate of plotted point
        :param y: y coordinate of plotted point
        :param colour: colour of plotted point
        """
        self.x = x
        self.y = y
        self.colour = colour


class VisualLabel:
    def __init__(self, text: str, x: int, y: int) -> None:
        """

        :param text: label text
        :param x: x coordinate of text
        :param y: y coordinate of text
        """
        self.text = text
        self.x = x
        self.y = y


class PygameGraphics:
    def __init__(self, get_nodes_paths_function) -> None:
        """

        :param get_nodes_paths_function: method of JuctionVisualiser for retrieving current nodes and current paths
        """

        self.get_nodes_paths_function = get_nodes_paths_function

        # Window Parameters
        self._window_width, self._window_height = 640, 695 # 1280, 1280
        self.scale = 100

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

        # Initialise Pygame
        pygame.init()
        window = pygame.display.set_mode(flags=pygame.HIDDEN)
        self.surface = pygame.Surface((self._window_width, self._window_height))
        # self.surface = pygame.Surface((self._window_width / 2, self._window_height / 2))

        # Grid Parameters
        self._grid_colour = (230, 230, 230)
        self._grid_range_x, self._grid_range_y = 10000, 10000
        self._grid_size = 100

        # Node Parameters
        self._node_diameter = 5
        self._node_colour = (0, 0, 255)
        self._tangent_scale = 0.1

        # Path Parameters
        self._path_colour = (0, 255, 0)
        self._hermite_path_points = []
        self._poly_path_points = []

        # Label parameters
        self._node_labels = []
        self._node_label_colour = (0, 0, 255)
        self._path_labels = []
        self._path_label_colour = (0, 255, 0)

    # Create a blank screen, set a center point pixel, check for events and calculate dragging
    def refresh(self, _draw_grid=False, _draw_hermite_paths=False, _draw_poly_paths=False, _draw_nodes=False, _draw_node_labels=False, _draw_path_labels=False, _draw_curvature=False):
        self.surface.fill((255, 255, 255))
        self.surface.set_at(self._position_offsetter(0, 0), (0, 0, 0))

        nodes, paths = self.get_nodes_paths_function()

        if _draw_grid: self.draw_grid()
        if _draw_hermite_paths: self.draw_hermite_paths(_draw_curvature)
        if _draw_poly_paths: self.draw_poly_paths(_draw_curvature)
        if _draw_nodes: self.draw_nodes(nodes)
        self.draw_labels(_draw_node_labels, _draw_path_labels)

    def calculate_scroll(self, mouse_event):
        if mouse_event.type() == QtCore.QEvent.MouseMove:
            pos = mouse_event.pos()
            self._mouse_position_x, self._mouse_position_y = pos.x(), pos.y()
        if mouse_event.type() == QtCore.QEvent.MouseButtonPress:
            self._scroll = True
            pos = mouse_event.pos()
            self._scroll_start_position_x, self._scroll_start_position_y = pos.x(), pos.y()
        if mouse_event.type() == QtCore.QEvent.MouseButtonRelease:
            self._scroll = False
            self._scroll_offset_x_old = self._scroll_offset_x
            self._scroll_offset_y_old = self._scroll_offset_y
        if self._scroll:
            self._scroll_offset_x = self._scroll_start_position_x - self._mouse_position_x + self._scroll_offset_x_old
            self._scroll_offset_y = self._scroll_start_position_y - self._mouse_position_y + self._scroll_offset_y_old

    # Draw nodes
    def draw_nodes(self, nodes):
        self._node_labels.clear()
        for _node in nodes:
            _center_point = self._position_offsetter(_node.x, _node.y)
            _node_tangents_x, _node_tangents_y = _node.get_tangents(200)
            _direction_point = self._position_offsetter(_node.x + round(self._tangent_scale * _node_tangents_x), _node.y + round(self._tangent_scale * _node_tangents_y))
            pygame.draw.circle(self.surface, self._node_colour, _center_point, radius=self._node_diameter, width=0)
            pygame.draw.line(self.surface, self._node_colour, _center_point, _direction_point, width=3)
            self._node_labels.append(VisualLabel(str(_node.uid), _node.x - (self._node_diameter + 5) * sin(_node.angle), _node.y + (self._node_diameter + 5) * cos(_node.angle)))

    # Draw paths
    def render_hermite_paths(self, paths):
        self._hermite_path_points.clear()
        self._path_labels.clear()
        _upper, _lower = self._calculate_hermite_path_curvature(paths)
        for _path in paths:
            if _path.get_distance() > 0:
                _path_length = round(_path.get_distance()*1.5) # Changing iteration intervals for improved performance
                for _i in range(_path_length+1):
                    _s = _i/_path_length
                    _x = _path.x_hermite_cubic_coeff[0] + _path.x_hermite_cubic_coeff[1]*_s + _path.x_hermite_cubic_coeff[2]*(_s*_s) + _path.x_hermite_cubic_coeff[3]*(_s*_s*_s)
                    _y = _path.y_hermite_cubic_coeff[0] + _path.y_hermite_cubic_coeff[1]*_s + _path.y_hermite_cubic_coeff[2]*(_s*_s) + _path.y_hermite_cubic_coeff[3]*(_s*_s*_s)
                    _path_colour = self._calculate_curvature_colour(_path, _i, _lower, _upper)
                    _x = round(_x)
                    _y = round(_y)
                    self._hermite_path_points.append(VisualPoint(_x, _y, _path_colour))
                    if _i == round(_path_length / 2):
                        self._path_labels.append(VisualLabel(str(_path.uid), _x + 5, _y + 5))

    def _calculate_hermite_path_curvature(self, paths):
        curvature = []
        for _path in paths:
            curvature += _path.curvature
        upper = sorted(curvature)[round(3 * len(curvature) / 4)]
        lower = sorted(curvature)[round(1 * len(curvature) / 4)]
        return upper, lower

    def _calculate_curvature_colour(self, path, i, lower, upper):
        if type(path.poly_coeff) is list:
            try:
                _colour_mag = round((self._clamp(path.curvature[i], lower, upper) - lower) * (255 / (upper - lower)))
            except ValueError:
                _colour_mag = 0
        else:
            _colour_mag = 0
        return _colour_mag, 255 - _colour_mag, 0

    def render_poly_paths(self, paths, draw_curvature=False):
        self._poly_path_points.clear()
        upper, lower = self._calculate_poly_path_curvature(paths)
        for _path in paths:
            if _path.get_distance() > 0:
                if type(_path.poly_coeff) is list:
                    for i in range(min(_path.start_node.x, _path.end_node.x) * 10, max(_path.start_node.x, _path.end_node.x) * 10):
                        _x = i / 10
                        _y = 0
                        for n, coef in enumerate(_path.poly_coeff):
                            _y += coef * pow(_x, _path.poly_order - n)
                        _path_colour = (0, 255, 0)  #self._calculate_curvature_colour(_path, _x, lower, upper)
                        _y = round(_y)
                        _x = round(_x)
                        self._poly_path_points.append(VisualPoint(_x, _y, _path_colour))
                else:
                    for _y in range(min(_path.start_node.y, _path.end_node.y), max(_path.start_node.y, _path.end_node.y)):
                        self._poly_path_points.append(VisualPoint(_path.poly_coeff, _y, (0, 255, 0)))

    def _calculate_poly_path_curvature(self, paths):
        curvature = []
        for _path in paths:
            if _path.get_distance() > 0:
                if type(_path.poly_coeff) is list:
                    for i in range(min(_path.start_node.x, _path.end_node.x) * 10, max(_path.start_node.x, _path.end_node.x) * 10):
                        x = i / 10
                        curvature.append(_path.calculate_curve_radius(x))
        if len(curvature) > 0:
            curvature.sort()
            upper = curvature[round(3 * len(curvature) / 4)]
            lower = curvature[round(1 * len(curvature) / 4)]
            return upper, lower
        else:
            return None, None

    # Offseting graphics for dragging
    def _position_offsetter(self, x, y):
        return x - self._scroll_offset_x, y - self._scroll_offset_y

    def _draw_paths(self, _paths_points, _draw_curvature):
        for _point in _paths_points:
            self.surface.set_at(self._position_offsetter(_point.x, _point.y), _point.colour if _draw_curvature else self._path_colour)

    def draw_hermite_paths(self, _draw_curvature):
        self._draw_paths(self._hermite_path_points, _draw_curvature)

    def draw_poly_paths(self, _draw_curvature):
        self._draw_paths(self._poly_path_points, _draw_curvature)

    def _clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)

    def draw_labels(self, _draw_node_labels=True, _draw_path_labels=True):
        if _draw_node_labels:
            for _node_label in self._node_labels:
                self._draw_text(_node_label.text, _node_label.x, _node_label.y, self._node_label_colour)
        if _draw_path_labels:
            for _path_label in self._path_labels:
                self._draw_text(_path_label.text, _path_label.x, _path_label.y, self._path_label_colour)

    # Draw text
    def _draw_text(self, text, x, y, colour=(0, 0, 0)):
        _font = pygame.font.Font(pygame.font.get_default_font(), 20)
        _text = _font.render(text, False, colour)
        self.surface.blit(_text, self._position_offsetter(x - round(_text.get_width() / 2), y))

    def get_click_position(self):
        x = self._mouse_position_x + self._scroll_offset_x
        y = self._mouse_position_y + self._scroll_offset_y
        return x, y

    def draw_grid(self):
        for x in range(0, self._grid_range_x, self._grid_size):
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(x, -self._grid_range_y), self._position_offsetter(x, self._grid_range_y))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-x, -self._grid_range_y), self._position_offsetter(-x, self._grid_range_y))

        for y in range(0, self._grid_range_y, self._grid_size):
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x, y), self._position_offsetter(self._grid_range_x, y))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x, -y), self._position_offsetter(self._grid_range_x, -y))

    def recenter(self):
        self._scroll_offset_x = -round(self._window_width / 2)
        self._scroll_offset_y = -round(self._window_height / 2)
        self._scroll_offset_x_old = self._scroll_offset_x
        self._scroll_offset_y_old = self._scroll_offset_y


