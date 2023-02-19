import pygame
from math import sin, cos, pi
from PyQt5 import QtCore
from Library.maths import clamp, VisualPoint
from copy import deepcopy as copy
import requests


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
    def __init__(self, window_width, window_height, model) -> None:
        """

        :param window_width: GUI window width for calculating surface size
        :param window_height: GUI window heigh for calculating surface size
        :param model: model
        """

        # Functions
        self.model = model

        # Window Parameters
        self._window_width, self._window_height = window_width, window_height
        self._surface_width, self._surface_height = round(self._window_width / 2), self._window_height
        self._scale = 0.2

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
        self._scroll_changed = True

        # Initialise Pygame
        pygame.init()
        window = pygame.display.set_mode(flags=pygame.HIDDEN)
        self.surface = pygame.Surface((self._surface_width, self._surface_height))
        self.prev_surface = self.surface

        # Background parameters
        self.background_colour = (255, 255, 255)

        # Map parameters
        self.map_surface = None
        self.map_surface_scaled = None
        self._map_scale = self._scale

        # Grid Parameters
        self._grid_colour = (230, 230, 230)
        self._grid_range_x, self._grid_range_y = 100, 100
        self._grid_size = 1

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
    def refresh(self, force_full_refresh, draw_map=False, draw_grid=False, draw_hermite_paths=False, draw_nodes=False, draw_vehicles=False, draw_node_labels=False, draw_path_labels=False, draw_curvature=False, draw_lights=False) -> None:
        """

        This function manages what "layers" are displayed on the pygame surface.
        :param draw_grid: boolean for enabling display of grid
        :param draw_hermite_paths: boolean for enabling display of hermite paths
        :param draw_nodes: boolean for enabling display of nodes
        :param draw_vehicles: boolean for enabling display of cars
        :param draw_node_labels: boolean for enabling display of node labels
        :param draw_path_labels: boolean for enabling display of path labels
        :param draw_curvature: boolean for enabling display of path curvature
        :return: None
        """

        if self._scroll_changed or force_full_refresh:

            self.surface.fill(self.background_colour)
            if draw_map: self.draw_map()
            if draw_grid: self._draw_grid()
            if draw_hermite_paths: self._draw_hermite_paths(draw_curvature)
            if draw_nodes: self._draw_nodes(self.model.nodes)
            pygame.draw.circle(self.surface, (0, 0, 0), self._position_offsetter(0, 0), 3)
            self._draw_labels(draw_node_labels, draw_path_labels)

            self.prev_surface = self.surface.copy()
            self._scroll_changed = False

        else:
            self.surface = self.prev_surface.copy()

        if draw_vehicles: self._draw_vehicles(self.model.vehicles)
        if draw_lights: self._draw_lights(self.model.lights)

    def efficient_refresh(self, draw_grid=False, draw_hermite_paths=False, draw_nodes=False, draw_vehicles=False, draw_node_labels=False, draw_path_labels=False, draw_curvature=False):
        if self._scroll_changed:
            nodes, paths, vehicles = self.model.nodes, self.model.paths, self.model.vehicles

            self.surface.fill(self.background_colour)

            if draw_grid: self._draw_grid()
            if draw_hermite_paths: self._draw_hermite_paths(draw_curvature)
            if draw_nodes: self._draw_nodes(nodes)
            pygame.draw.circle(self.surface, (0, 0, 0), self._position_offsetter(0, 0), 3)
            self._draw_labels(draw_node_labels, draw_path_labels)

            self.prev_surface = self.surface

            self._scroll_changed = False
        else:
            self.surface = self.prev_surface
        if draw_vehicles: self._draw_vehicles(vehicles)

    def highlight_paths(self, paths: list) -> None:
        """

        Renders and shows just the paths in the list
        :param paths: list of paths to display
        :return: None
        """
        self.surface.fill((255, 255, 255))
        pygame.draw.circle(self.surface, (0, 0, 0), self._position_offsetter(0, 0), 3)

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
            if path.get_euclidean_distance(self.model) > 0:
                path_length = round(path.get_euclidean_distance(self.model) * 150)  # Changing iteration intervals for improved performance
                for i in range(path_length+1):
                    s = i/path_length
                    x, y = path.calculate_coords(s)
                    x *= 100
                    y *= 100
                    path_colour = self._calculate_curvature_colour(path, s, lower, upper)
                    x = round(x)
                    y = round(y)
                    self._hermite_path_points.append(VisualPoint(x, y, path_colour))
                    if i == round(path_length / 2):
                        self._path_labels.append(VisualLabel(str(path.uid), x + 5, y + 5))

    def _calculate_hermite_path_curvature(self, paths: list) -> tuple:
        """

        :param paths: list of all paths
        :return: Returns the highest and curvature and lowest curvature of all paths
        """
        curvature = []
        for path in paths:
            curvature += path.get_all_curvature()
        upper = sorted(curvature)[round(3 * len(curvature) / 4)]
        lower = sorted(curvature)[round(1 * len(curvature) / 4)]
        return upper, lower

    # Functions for drawing both Hermite and Poly paths
    def _draw_paths(self, paths_points, draw_curvature, highlight: bool = False) -> None:
        """

        :param paths_points: points to be drawn on the path
        :param draw_curvature: boolean to enable curvature coloring of drawn paths
        :param highlight: highlight the paths in pink colour
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
    def _calculate_curvature_colour(self, path, s: float, lower: float, upper: float) -> tuple:
        """

        :param path: singular path object
        :param s: s term
        :param lower: lowest path curve radius
        :param upper: highest path curve radius
        :return: colour based on curve radius at path curvature array index
        """
        if upper == lower:
            colour_mag = 0
        else:
            colour_mag = round((clamp(path.calculate_curvature(s), lower, upper) - lower) * (255 / (upper - lower)))
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
            x = node.x * 100
            y = node.y * 100

            center_point = self._position_offsetter(x, y)
            node_tangents_x, _node_tangents_y = node.get_tangents(200)
            direction_point = self._position_offsetter(x + round(self._tangent_scale * node_tangents_x / self._scale), y + round(self._tangent_scale * _node_tangents_y / self._scale))
            pygame.draw.circle(self.surface, self._node_colour, center_point, radius=self._node_diameter, width=0)
            pygame.draw.line(self.surface, self._node_colour, center_point, direction_point, width=3)
            self._node_labels.append(VisualLabel(str(node.uid), x - (self._node_diameter + 5) * sin(node.angle), y + (self._node_diameter + 5) * cos(node.angle)))

    def _draw_labels(self, draw_node_labels=True, draw_path_labels=True) -> None:
        """

        Draw all labels on pygame surface
        :param draw_node_labels: boolean to enable drawing of node labels
        :param draw_path_labels: boolean to enable drawing of path labels
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
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(x * 100, -self._grid_range_y * 100), self._position_offsetter(x * 100, self._grid_range_y * 100))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-x * 100, -self._grid_range_y * 100), self._position_offsetter(-x * 100, self._grid_range_y * 100))

        for y in range(0, self._grid_range_y, self._grid_size):
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x * 100, y * 100), self._position_offsetter(self._grid_range_x * 100, y * 100))
            pygame.draw.line(self.surface, self._grid_colour, self._position_offsetter(-self._grid_range_x * 100, -y * 100), self._position_offsetter(self._grid_range_x * 100, -y * 100))

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
            self._scroll_changed = True
            self._scroll = True
            pos = mouse_event.pos()
            self._scroll_start_position_x, self._scroll_start_position_y = pos.x(), pos.y()
        if mouse_event.type() == QtCore.QEvent.MouseButtonRelease:
            self._scroll = False
            self._scroll_changed = True
            self._scroll_offset_x_old = self._scroll_offset_x
            self._scroll_offset_y_old = self._scroll_offset_y
        if self._scroll:
            self._scroll_changed = True
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

    def _draw_vehicles(self, vehicles: list) -> None:
        """

        Draws cars
        :param cars: list of car x,y coordinates
        :return: None
        """
        for vehicle in vehicles:
            x, y = self._position_offsetter(vehicle[0] * 100, vehicle[1] * 100)
            if len(vehicle) > 2:
                if len(vehicle) > 4:
                    vehicle_length = vehicle[3] * 100
                    vehicle_width = vehicle[4] * 100
                else:
                    vehicle_length = 400
                    vehicle_width = 200

                vehicle_size_x = vehicle_length * self._scale
                vehicle_size_y = vehicle_width * self._scale
                rectangle_surface = pygame.Surface((vehicle_size_x, vehicle_size_y))
                rectangle_surface.set_colorkey((0, 0, 0))
                pygame.draw.rect(rectangle_surface, (255, 130, 0), (0, 0, vehicle_size_x, vehicle_size_y))
                rectangle_surface = pygame.transform.rotate(rectangle_surface, 180 * -vehicle[2] / pi)
                self.surface.blit(rectangle_surface, (x - round(rectangle_surface.get_width() / 2), y - round(rectangle_surface.get_height() / 2)))
            else:
                pygame.draw.circle(self.surface, (100, 100, 100), (x, y), 1)

    def _draw_lights(self, traffic_lights: list) -> None:
        light_colours = []

        for traffic_light in traffic_lights:
            for path_uid in traffic_light.path_uids:
                path = self.model.get_path(path_uid)

                if path.start_node_uid in [light.node_uid for light in light_colours]:
                    for light in light_colours:
                        if light.node_uid == path.start_node_uid:
                            light.add_colour(traffic_light.colour)
                            break
                else:
                    light_colours.append(LightColour(path.start_node_uid, traffic_light.colour))

        for light in light_colours:
            node = self.model.get_node(light.node_uid)

            x, y = self._position_offsetter(node.x * 100, node.y * 100)
            pygame.draw.rect(self.surface, (0, 0, 0), (x - round((len(light.colours) * 10) / 2), y + 10, len(light.colours) * 10, 30))

            for index, colour in enumerate(light.colours):
                position_offset = round((-((len(light.colours) - 1) * 25) / 2) + index * 25)

                red_rgb = (100, 0, 0)
                amber_rgb = (50, 50, 0)
                green_rgb = (0, 100, 0)

                if colour == "green":
                    red_rgb = (50, 0, 0)
                    amber_rgb = (50, 50, 0)
                    green_rgb = (0, 200, 0)
                elif colour == "amber":
                    red_rgb = (50, 0, 0)
                    amber_rgb = (255, 200, 0)
                    green_rgb = (0, 50, 0)
                elif colour == "red":
                    red_rgb = (255, 0, 0)
                    amber_rgb = (50, 50, 0)
                    green_rgb = (0, 50, 0)
                elif colour == "red_amber":
                    red_rgb = (255, 0, 0)
                    amber_rgb = (255, 200, 0)
                    green_rgb = (0, 50, 0)

                pygame.draw.circle(self.surface, red_rgb, self._position_offsetter((node.x * 100) + position_offset, (node.y * 100) + 37), 3)
                pygame.draw.circle(self.surface, amber_rgb, self._position_offsetter((node.x * 100) + position_offset, (node.y * 100) + 60), 3)
                pygame.draw.circle(self.surface, green_rgb, self._position_offsetter((node.x * 100) + position_offset, (node.y * 100) + 83), 3)

    def draw_map(self):
        if self.map_surface is not None:

            self.map_surface_scaled = pygame.transform.scale(self.map_surface, (self._surface_width * self._scale * self._map_scale, self._surface_height * self._scale * self._map_scale))
            self.surface.blit(self.map_surface_scaled, (-self._scroll_offset_x - round(self.map_surface_scaled.get_width() / 2), -self._scroll_offset_y - round(self.map_surface_scaled.get_height() / 2)))  # paint to screen

    def update_map_image(self, latitude, longitude, heading, scale, key):
        width = round((500 / self._surface_height) * self._surface_width)
        request_scale = 19
        URL = "https://maps.googleapis.com/maps/api/staticmap?" + "center=" + str(longitude) + "," + str(latitude) + "&zoom=" + str(request_scale) + "&size=" + str(width) + "x" + str(500) + "&maptype=satellite&key=" + key
        response = requests.get(URL)
        with open('background.png', 'wb') as file:
            file.write(response.content)
        self.map_surface = pygame.image.load("background.png").convert()
        self.map_surface = pygame.transform.rotate(self.map_surface, heading)
        self._map_scale = scale
        self.map_surface_scaled = pygame.transform.scale(self.map_surface, (self._surface_width * self._scale * self._map_scale, self._surface_height * self._scale * self._map_scale))


class LightColour:
    def __init__(self, node_uid, initial_color=None):
        self.node_uid = node_uid
        self.colours = []
        if initial_color is not None:
            self.add_colour(initial_color)

    def add_colour(self, colour):
        self.colours.append(colour)






