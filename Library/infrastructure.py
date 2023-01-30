import math
import random
from math import sin, cos, sqrt, atan
from Library.maths import Vector, calculate_cross_product, calculate_vector_magnitude
from typing import List

class Node:
    def __init__(self, uid: int, x: float, y: float, angle: float):
        self.uid = uid
        self.x = x
        self.y = y
        self.angle = angle

    def get_tangents(self, _weight=None):
        tx = _weight * sin(self.angle)
        ty = -_weight * cos(self.angle)
        return tx, ty


class Path:
    def __init__(self, uid: int, start_node: Node, end_node: Node, discrete_length_increment_size=0.01, discrete_iteration_qty=100000):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_node
        self.x_hermite_cubic_coeff = []
        self.y_hermite_cubic_coeff = []

        self.discrete_length_increment_size = discrete_length_increment_size
        self.discrete_iteration_qty = discrete_iteration_qty

        self.discrete_path = []
        self.curvature = []

        # self.calculate_all()

    # Gets
    def get_euclidean_distance(self, model):
        start_node = model.get_node(self.start_node)
        end_node = model.get_node(self.end_node)
        return sqrt((start_node.x - end_node.x) ** 2 + (start_node.y - end_node.y) ** 2)

    def get_s(self, arc_length: float):
        arc_length = round(arc_length * (1 / self.discrete_length_increment_size))
        return self.discrete_path[arc_length][0]

    def get_coordinates(self, arc_length: float):
        arc_length = round(arc_length / self.discrete_length_increment_size)
        if arc_length >= len(self.discrete_path):
            return None
        else:
            return self.discrete_path[arc_length][1], self.discrete_path[arc_length][2]

    def get_direction(self, arc_length: float):
        arc_length = round(arc_length / self.discrete_length_increment_size)
        return self.discrete_path[arc_length][3]

    def get_curvature(self, arc_length: float):
        arc_length = round(arc_length / self.discrete_length_increment_size)
        return self.discrete_path[arc_length][4]

    def get_all_s(self):
        return [point[0] for point in self.discrete_path]

    def get_all_coords(self):
        return [[point[1], point[2]] for point in self.discrete_path]

    def get_all_direction(self):
        return [point[3] for point in self.discrete_path]

    def get_all_curvature(self):
        return [point[4] for point in self.discrete_path]

    # Discrete Calculations

    def calculate_all(self, model):
        self.calculate_hermite_spline_coefficients(model)
        self.calculate_discrete_arc_length_points()
        self.calculate_discrete_direction_points()
        self.calculate_discrete_curvature_points()

    def calculate_hermite_spline_coefficients(self, model):
        start_node = model.get_node(self.start_node)
        end_node = model.get_node(self.end_node)
        p1x = start_node.x
        p1y = start_node.y
        p1tx, p1ty = start_node.get_tangents(self.get_euclidean_distance(model) * 1.5)
        p2x = end_node.x
        p2y = end_node.y
        p2tx, p2ty = end_node.get_tangents(self.get_euclidean_distance(model) * 1.5)
        p2tx = -p2tx
        p2ty = -p2ty
        self.x_hermite_cubic_coeff = [p1x, p1tx, -3 * p1x + 3 * p2x - 2 * p1tx + p2tx, 2 * p1x - 2 * p2x + p1tx - p2tx]
        self.y_hermite_cubic_coeff = [p1y, p1ty, -3 * p1y + 3 * p2y - 2 * p1ty + p2ty, 2 * p1y - 2 * p2y + p1ty - p2ty]

    def calculate_discrete_arc_length_points(self):
        x_start, y_start = self.calculate_coords(0)
        self.discrete_path = [[0, x_start, y_start]]
        for iteration in range(1, self.discrete_iteration_qty + 1):
            s = iteration / self.discrete_iteration_qty
            x1, y1 = self.calculate_coords(s)
            x0, y0 = self.discrete_path[-1][1], self.discrete_path[-1][2]
            distance = sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)
            if abs(distance) >= self.discrete_length_increment_size:
                self.discrete_path.append([s, x1, y1])

    def calculate_discrete_direction_points(self):
        for index, point in enumerate(self.discrete_path):
            direction = self.calculate_direction(point[0])
            self.discrete_path[index].append(direction)

    def calculate_discrete_curvature_points(self):
        for index, point in enumerate(self.discrete_path):
            curvature = self.calculate_curvature(point[0])
            self.discrete_path[index].append(curvature)

    # Hermite Calculations

    def calculate_coords(self, s: float):
        x = self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + self.x_hermite_cubic_coeff[2] * (s * s) + self.x_hermite_cubic_coeff[3] * (s * s * s)
        y = self.y_hermite_cubic_coeff[0] + self.y_hermite_cubic_coeff[1] * s + self.y_hermite_cubic_coeff[2] * (s * s) + self.y_hermite_cubic_coeff[3] * (s * s * s)
        return x, y

    def calculate_direction(self, s: float):
        dy_ds = self.y_hermite_cubic_coeff[1] + 2 * self.y_hermite_cubic_coeff[2] * s + 3 * self.y_hermite_cubic_coeff[3] * s * s
        dx_ds = self.x_hermite_cubic_coeff[1] + 2 * self.x_hermite_cubic_coeff[2] * s + 3 * self.x_hermite_cubic_coeff[3] * s * s
        if dx_ds != 0 :
            dy_dx = dy_ds / dx_ds
            a = 90-atan(dy_dx)
        else:
            if dy_ds > 0:
                a = 0
            else:
                a = 180
        return a

    def calculate_curvature(self, s: float):
        ## Source: https://math.libretexts.org/Bookshelves/Calculus/Supplemental_Modules_(Calculus)/Vector_Calculus/2%3A_Vector-Valued_Functions_and_Motion_in_Space/2.3%3A_Curvature_and_Normal_Vectors_of_a_Curve

        dy_ds = self.y_hermite_cubic_coeff[1] + 2 * self.y_hermite_cubic_coeff[2] * s + 3 * self.y_hermite_cubic_coeff[3] * s * s
        dy2_ds2 = 2 * self.y_hermite_cubic_coeff[2] + 6 * self.y_hermite_cubic_coeff[3] * s

        dx_ds = self.x_hermite_cubic_coeff[1] + 2 * self.x_hermite_cubic_coeff[2] * s + 3 * self.x_hermite_cubic_coeff[3] * (s * s)
        dx2_ds2 = 2 * self.x_hermite_cubic_coeff[2] + 6 * self.x_hermite_cubic_coeff[3] * s

        dR_ds = Vector(dx_ds, dy_ds, 0)
        dR2_ds2 = Vector(dx2_ds2, dy2_ds2, 0)

        c = calculate_vector_magnitude(calculate_cross_product(dR_ds, dR2_ds2)) / (calculate_vector_magnitude(dR_ds)**3)
        return c

    def get_length(self):
        return len(self.discrete_path) * self.discrete_length_increment_size


class Route:
    def __init__(self, uid: int, paths: List[Path]):
        discrete_length_increment_sizes = [path.discrete_length_increment_size for path in paths]
        assert discrete_length_increment_sizes.count(discrete_length_increment_sizes[0]) == len(
            discrete_length_increment_sizes)
        self.discrete_length_increment_size = discrete_length_increment_sizes[0]

        self.uid = uid
        self.length = 0.0
        for path in paths:
            self.length += path.get_length()
        self._paths = paths
        self._path_uids = [path.uid for path in paths]

    def get_coordinates(self, route_distance_travelled: float):
        path, index = self.get_path_and_index(route_distance_travelled)
        return path.discrete_path[index][1], path.discrete_path[index][2]

    def get_curvature(self, route_distance_travelled: float):
        path, index = self.get_path_and_index(route_distance_travelled)
        return path.discrete_path[index][4]

    def get_path(self, route_distance_travelled: float):
        path, _ = self.get_path_and_index(route_distance_travelled)
        return path

    def get_path_uids(self):
        return self._path_uids

    def get_route_distance_travelled_to_path(self, path_uid):
        assert path_uid in self.get_path_uids()
        distance_travelled = 0.0
        for path in self._paths:
            if path.uid == path_uid:
                return distance_travelled
            else:
                distance_travelled += path.get_length()

    def get_path_and_path_distance_travelled(self, route_distance_travelled: float):
        index = math.floor(route_distance_travelled / self.discrete_length_increment_size)
        index_offset = 0
        for path in self._paths:
            path_length = len(path.discrete_path)
            if index_offset + path_length <= index:
                index_offset += path_length
                continue
            else:
                return path, (index - index_offset) * self.discrete_length_increment_size

    def get_path_and_index(self, route_distance_travelled: float):
        index = math.floor(route_distance_travelled / self.discrete_length_increment_size)
        index_offset = 0
        for path in self._paths:
            path_length = len(path.discrete_path)
            if index_offset + path_length <= index:
                index_offset += path_length
                continue
            else:
                return path, index - index_offset


class TrafficLight:
    def __init__(self, uid, path_uid: int, cycle_length: float = 12.0, cycle_green: float = 0.5) -> None:
        """

        :param cycle_length: time it takes for the traffic light to complete a single light cycle [s]
        :param cycle_red: red state fraction of the cycle length
        :param cycle_yellow: yellow state fraction of the cycle length
        :param distance_traveled: position of the traffic light along the path [m]
        """

        self.uid = uid
        self.path_uid = path_uid[0]
        self.route_distance_travelled = None
        self.color = "green"
        self.cycle_time = 0.0

        assert 0.0 <= cycle_green <= 1.0
        self.cycle_green = cycle_green
        self.cycle_length = cycle_length

    def set_state(self, color: str):
        if color == "green":
            self.cycle_time = 0.0
            self.color = "green"
        elif color == "red":
            self.cycle_time = self.cycle_length * self.cycle_green
            self.color = "red"

    def update(self, time_delta: float = 0.1) -> None:
        """

        :rtype: None
        :param time_delta: iteration length [s]
        """
        self.cycle_time += time_delta
        if self.cycle_time < self.cycle_green * self.cycle_length:
            self.color = "green"
        elif self.cycle_time < self.cycle_length:
            self.color = "red"
        else:
            self.cycle_time = 0.0

    def get_velocity(self) -> float:
        return 0.0

    def get_length(self) -> float:
        return 0.0

    def allows_traffic(self) -> bool:
        if self.color == "red":
            return False
        elif self.color == "green":
            return True
