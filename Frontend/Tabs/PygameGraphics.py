import pygame
from math import sin, cos
from PyQt5 import QtCore
from Library.maths import clamp, VisualPoint


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
    def __init__(self, window_width, window_height, get_data_function) -> None:
        """

        :param window_width: GUI window width for calculating surface size
        :param window_height: GUI window heigh for calculating surface size
        :param get_data_function: method of JuctionVisualiser for retrieving current nodes and current paths
        """

        # Functions
        self.get_data_function = get_data_function

        # Window Parameters
        self._window_width, self._window_height = window_width, window_height
        self._surface_width, self._surface_height = round(self._window_width / 2), self._window_height
        self._scale = 0.5

        # Scroll Parameters
        self._mouse_position_x = 0
        self._mouse_position_y = 0
        self._scroll_offset_x = -round(self._surface_width / 2)
        self._scroll_offset_y = -round(self._surface_height / 2)
        self._scroll_offset_x_old = self._scroll_offset_x
        self._scroll_offset_y_old = self._scroll_offset_y
        self._scroll = False
        self._scroll_start_position_x = 0
        self._scroll_start_position_y = 0

        # Initialise Pygame
        pygame.init()
        window = pygame.display.set_mode(flags=pygame.HIDDEN)
        self.surface = pygame.Surface((self._surface_width, self._surface_height))
        # self.surface = pygame.Surface((self._surface_width / 2, self._surface_height / 2))

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
        self._path_highlight_colour = (255, 0, 255)
        self._hermite_path_points = []

        # Label parameters
        self._node_labels = []
        self._node_label_colour = (0, 0, 255)
        self._path_labels = []
        self._path_label_colour = (0, 255, 0)

    # Main function for drawing paths (from renders), nodes, labels, grid etc.
    def refresh(self, draw_grid=False, draw_hermite_paths=False, draw_nodes=False, draw_cars=False, draw_node_labels=False, draw_path_labels=False, draw_curvature=False) -> None:
        """

        This function manages what "layers" are displayed on the pygame surface.
        :param draw_grid: boolean for enabling display of grid
        :param draw_hermite_paths: boolean for enabling display of hermite paths
        :param draw_poly_paths: boolean for enabling display of poly paths
        :param draw_nodes: boolean for enabling display of nodes
        :param draw_node_labels: boolean for enabling display of node labels
        :param draw_path_labels: boolean for enabling display of path labels
        :param draw_curvature: boolean for enabling display of path curvature
        :return: None
        """
        self.surface.fill((255, 255, 255))
        self.surface.set_at(self._position_offsetter(0, 0), (0, 0, 0))

        nodes, paths, cars = self.get_data_function()

        if draw_grid: self._draw_grid()
        if draw_hermite_paths: self._draw_hermite_paths(draw_curvature)
        if draw_nodes: self._draw_nodes(nodes)
        if draw_cars: self._draw_cars(cars)
        self._draw_labels(draw_node_labels, draw_path_labels)

    def highlight_paths(self, paths: list) -> None:
        """

        Renders and shows just the paths in the list
        :param paths: list of paths to display
        :return: None
        """
        self.surface.fill((255, 255, 255))
        self.surface.set_at(self._position_offsetter(0, 0), (0, 0, 0))

        self.render_hermite_paths(paths)
        self._draw_hermite_paths(False, highlight=True)
        self._draw_labels(False, True)

    # Functions for rendering Hermite paths
    def render_hermite_paths(self, paths: list) -> None:
        """

        Calculates and saves a list of all points that should be drawn for displaying all hermite paths
        :param paths: list of hermite paths
        :return: None
        """
        self._hermite_path_points.clear()
        self._path_labels.clear()
        upper, lower = self._calculate_hermite_path_curvature(paths)
        for path in paths:
            if path.get_euclidean_distance() > 0:
                path_length = round(path.get_euclidean_distance() * 1.5)  # Changing iteration intervals for improved performance
                for i in range(path_length+1):
                    s = i/path_length
                    x = path.x_hermite_cubic_coeff[0] + path.x_hermite_cubic_coeff[1]*s + path.x_hermite_cubic_coeff[2]*(s*s) + path.x_hermite_cubic_coeff[3]*(s*s*s)
                    y = path.y_hermite_cubic_coeff[0] + path.y_hermite_cubic_coeff[1]*s + path.y_hermite_cubic_coeff[2]*(s*s) + path.y_hermite_cubic_coeff[3]*(s*s*s)
                    path_colour = self._calculate_curvature_colour(path, i, lower, upper)
                    x = round(x)
                    y = round(y)
                    self._hermite_path_points.append(VisualPoint(x, y, path_colour))
                    if i == round(path_length / 2):
                        self._path_labels.append(VisualLabel(str(path.uid), x + 5, y + 5))

    def _calculate_hermite_path_curvature(self, paths: list) -> tuple:
        curvature = []
        for path in paths:
            curvature += path.curvature
        upper = sorted(curvature)[round(3 * len(curvature) / 4)]
        lower = sorted(curvature)[round(1 * len(curvature) / 4)]
        return upper, lower

    # Functions for drawing both Hermite and Poly paths
    def _draw_paths(self, paths_points, draw_curvature, highlight: bool = False) -> None:
        """

        :param paths_points: points to be drawn on the path
        :param draw_curvature: boolean to enable curvature coloring of drawn paths
        :return: None
        """
        for point in paths_points:
            point_colour = self._path_colour
            if highlight:
                point_colour = self._path_highlight_colour
            elif draw_curvature:
                point_colour = point.colour
            self.surface.set_at(self._position_offsetter(point.x, point.y), point_colour)

    def _draw_hermite_paths(self, draw_curvature: bool, highlight: bool = False) -> None:
        """

        :param draw_curvature: boolean to enable curvature coloring of drawn hermite paths
        :return: None
        """
        self._draw_paths(self._hermite_path_points, draw_curvature, highlight)

    # Path drawing math functions
    def _calculate_curvature_colour(self, path, i: int, lower: float, upper: float) -> tuple:
        """

        :param path: singular path object
        :param i: curvature array index in path object
        :param lower: lowest path curve radius
        :param upper: highest path curve radius
        :return: colour based on curve radius at path curvature array index
        """
        # if type(path.poly_coeff) is list:
        #     try:
        #         colour_mag = round((self._clamp(path.curvature[i], lower, upper) - lower) * (255 / (upper - lower)))
        #     except ValueError:
        #         colour_mag = 0
        # else:
        #     colour_mag = 0
        colour_mag = 0
        return colour_mag, 255 - colour_mag, 0

    def _position_offsetter(self, x: int, y: int) -> tuple:
        """

        Translate coordinates based on the scroll position of the pygame surface
        :param x: x coordinate
        :param y: y coordinate
        :return: translated coordinates
        """

        x = round(x * self._scale) - self._scroll_offset_x
        y = round(y * self._scale) - self._scroll_offset_y

        return x, y

    # Other drawing functions

    def _draw_nodes(self, nodes: list) -> None:
        """

        :param nodes: list of nodes to draw
        :return: None
        """
        self._node_labels.clear()
        for node in nodes:
            center_point = self._position_offsetter(node.x, node.y)
            node_tangents_x, _node_tangents_y = node.get_tangents(200)
            direction_point = self._position_offsetter(node.x + round(self._tangent_scale * node_tangents_x),
                                                       node.y + round(self._tangent_scale * _node_tangents_y))
            pygame.draw.circle(self.surface, self._node_colour, center_point, radius=self._node_diameter, width=0)
            pygame.draw.line(self.surface, self._node_colour, center_point, direction_point, width=3)
            self._node_labels.append(VisualLabel(str(node.uid), node.x - (self._node_diameter + 5) * sin(node.angle),
                                                 node.y + (self._node_diameter + 5) * cos(node.angle)))

    def _draw_labels(self, draw_node_labels=True, draw_path_labels=True) -> None:
        """

        Draw all labels on pygame surface
        :param _draw_node_labels: boolean to enable drawing of node labels
        :param _draw_path_labels: boolean to enable drawing of path labels
        :return:
        """
        if draw_node_labels:
            for node_label in self._node_labels:
                self._draw_text(node_label.text, node_label.x, node_label.y, self._node_label_colour)
        if draw_path_labels:
            for path_label in self._path_labels:
                self._draw_text(path_label.text, path_label.x, path_label.y, self._path_label_colour)

    def _draw_text(self, text, x, y, colour=(0, 0, 0)) -> None:
        """

        :param text: string of text to draw
        :param x: x location of text to be drawn
        :param y: y location of text to be drawn
        :param colour: colour of text
        :return: None
        """
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text = font.render(text, False, colour)
        self.surface.blit(text, self._position_offsetter(x - round(text.get_width() / 2), y))

    def _draw_grid(self) -> None:
        """

        Draws a grid of specified spacing (self._grid_size) starting from (0,0) within the grid range specified on the
        pygame surface
        :return: None
        """
        for x in range(0, self._grid_range_x, self._grid_size):
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(x, -self._grid_range_y), self._position_offsetter(x, self._grid_range_y))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-x, -self._grid_range_y), self._position_offsetter(-x, self._grid_range_y))

        for y in range(0, self._grid_range_y, self._grid_size):
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x, y), self._position_offsetter(self._grid_range_x, y))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x, -y), self._position_offsetter(self._grid_range_x, -y))

    # Mouse actions

    def calculate_scroll(self, mouse_event) -> None:
        """

        Calculate different actions to take for different mouse events. This includes:
        Clicking, clicking and dragging, clicking-dragging and releasing.
        :param mouse_event: mouse event from PyQT
        :return: None
        """
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

    def get_click_position(self) -> tuple:
        """

        :return: x and y coordinates of the junction coordinate that was clicked on
        """
        x = self._mouse_position_x + self._scroll_offset_x
        y = self._mouse_position_y + self._scroll_offset_y
        return x, y

    def recenter(self) -> None:
        """

        Re-center the window
        :return: None
        """
        self._scroll_offset_x = -round(self._surface_width / 2)
        self._scroll_offset_y = -round(self._surface_height / 2)
        self._scroll_offset_x_old = self._scroll_offset_x
        self._scroll_offset_y_old = self._scroll_offset_y

    def set_scale(self, scale: int) -> None:
        """

        Public function to set scale
        :param scale:
        :return: None
        """
        self._scale = scale

    def _draw_cars(self, cars):
        for car in cars:
            x, y = self._position_offsetter(car[0], car[1])
            pygame.draw.circle(self.surface, (255, 130, 0), (x, y), 5)


