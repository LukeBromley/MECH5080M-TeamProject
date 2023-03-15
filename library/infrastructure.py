import math
import random
from math import sin, cos, sqrt, atan, pi
from library.maths import Vector, calculate_cross_product, calculate_vector_magnitude
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
    def __init__(self, uid: int, start_node_uid: int, end_node_uid: int, discrete_length_increment_size=0.01, discrete_iteration_qty=100000, parallel_paths: List = []):
        self.uid = uid
        self.start_node_uid = start_node_uid
        self.end_node_uid = end_node_uid
        self.x_hermite_cubic_coeff = []
        self.y_hermite_cubic_coeff = []

        self.discrete_length_increment_size = discrete_length_increment_size
        self.discrete_iteration_qty = discrete_iteration_qty

        self.discrete_path = []
        self.curvature = []
        self.parallel_paths = parallel_paths

    # Gets
    def get_euclidean_distance(self, model):
        start_node = model.get_node(self.start_node_uid)
        end_node = model.get_node(self.end_node_uid)
        return sqrt((start_node.x - end_node.x) ** 2 + (start_node.y - end_node.y) ** 2)

    def get_s(self, arc_length: float):
        arc_length = round(
            arc_length * (1 / self.discrete_length_increment_size))
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

    def get_arc_length_from_s(self, s: float):
        if s == 0:
            return 0

        for index in range(1, len(self.discrete_path)):
            if self.discrete_path[index][0] > s:
                pos_dif = abs(self.discrete_path[index][0] - s)
                neg_dif = abs(self.discrete_path[index - 1][0] - s)
                if pos_dif < neg_dif:
                    return index * self.discrete_length_increment_size
                else:
                    return (index - 1) * self.discrete_length_increment_size
        return self.get_length()

    def get_coordinates_from_s(self, s: float):
        for index, discrete_point in enumerate(self.discrete_path):
            if discrete_point[0] > s:
                return discrete_point[1], discrete_point[2]
        return self.discrete_path[-1][1], self.discrete_path[-1][2]

    def get_all_s(self):
        return [point[0] for point in self.discrete_path]

    def get_all_coords(self):
        return [[point[1], point[2]] for point in self.discrete_path]

    def get_all_direction(self):
        return [point[3] for point in self.discrete_path]

    def get_all_curvature(self):
        return [point[4] for point in self.discrete_path]

    def get_length(self):
        return (len(self.discrete_path) - 1) * self.discrete_length_increment_size

    # Discrete Calculations

    def calculate_all(self, model):
        self.calculate_hermite_spline_coefficients(model)
        self.calculate_discrete_arc_length_points()
        self.calculate_discrete_direction_points()
        self.calculate_discrete_curvature_points()

    def calculate_hermite_spline_coefficients(self, model):
        start_node = model.get_node(self.start_node_uid)
        end_node = model.get_node(self.end_node_uid)
        p1x = start_node.x
        p1y = start_node.y
        p1tx, p1ty = start_node.get_tangents(
            self.get_euclidean_distance(model) * 1.5)
        p2x = end_node.x
        p2y = end_node.y
        p2tx, p2ty = end_node.get_tangents(
            self.get_euclidean_distance(model) * 1.5)
        p2tx = -p2tx
        p2ty = -p2ty
        self.x_hermite_cubic_coeff = [
            p1x, p1tx, -3 * p1x + 3 * p2x - 2 * p1tx + p2tx, 2 * p1x - 2 * p2x + p1tx - p2tx]
        self.y_hermite_cubic_coeff = [
            p1y, p1ty, -3 * p1y + 3 * p2y - 2 * p1ty + p2ty, 2 * p1y - 2 * p2y + p1ty - p2ty]

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
        x = self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + \
            self.x_hermite_cubic_coeff[2] * (s * s) + \
            self.x_hermite_cubic_coeff[3] * (s * s * s)
        y = self.y_hermite_cubic_coeff[0] + self.y_hermite_cubic_coeff[1] * s + \
            self.y_hermite_cubic_coeff[2] * (s * s) + \
            self.y_hermite_cubic_coeff[3] * (s * s * s)
        return x, y

    def calculate_direction(self, s: float):
        dy_ds = self.y_hermite_cubic_coeff[1] + 2 * self.y_hermite_cubic_coeff[2] * \
            s + 3 * self.y_hermite_cubic_coeff[3] * s * s
        dx_ds = self.x_hermite_cubic_coeff[1] + 2 * self.x_hermite_cubic_coeff[2] * \
            s + 3 * self.x_hermite_cubic_coeff[3] * s * s
        if dx_ds != 0:
            dy_dx = dy_ds / dx_ds
            a = atan(dy_dx)
        else:
            a = pi / 2
        return a

    def calculate_curvature(self, s: float):
        # Source: https://math.libretexts.org/Bookshelves/Calculus/Supplemental_Modules_(Calculus)/Vector_Calculus/2%3A_Vector-Valued_Functions_and_Motion_in_Space/2.3%3A_Curvature_and_Normal_Vectors_of_a_Curve

        dy_ds = self.y_hermite_cubic_coeff[1] + 2 * self.y_hermite_cubic_coeff[2] * \
            s + 3 * self.y_hermite_cubic_coeff[3] * s * s
        dy2_ds2 = 2 * \
            self.y_hermite_cubic_coeff[2] + 6 * \
            self.y_hermite_cubic_coeff[3] * s

        dx_ds = self.x_hermite_cubic_coeff[1] + 2 * self.x_hermite_cubic_coeff[2] * \
            s + 3 * self.x_hermite_cubic_coeff[3] * (s * s)
        dx2_ds2 = 2 * \
            self.x_hermite_cubic_coeff[2] + 6 * \
            self.x_hermite_cubic_coeff[3] * s

        dR_ds = Vector(dx_ds, dy_ds, 0)
        dR2_ds2 = Vector(dx2_ds2, dy2_ds2, 0)

        c = calculate_vector_magnitude(calculate_cross_product(
            dR_ds, dR2_ds2)) / (calculate_vector_magnitude(dR_ds)**3)
        return c


class Route:
    def __init__(self, uid: int, path_uids: list, length: float):
        self.uid = uid
        self._path_uids = path_uids
        self.length = length

    def get_path_uids(self):
        return self._path_uids

    def get_path_uid(self, index: int):
        return self._path_uids[index]


class TrafficLight:
    def __init__(self, uid, path_uids: list) -> None:
        """

        :param cycle_length: time it takes for the traffic light to complete a single light cycle [s]
        :param cycle_red: red state fraction of the cycle length
        :param cycle_yellow: yellow state fraction of the cycle length
        :param distance_traveled: position of the traffic light along the path [m]
        """

        self.uid = uid
        self.path_uids = path_uids
        self.colour = "green"
        assert self.colour == "green" or self.colour == "amber" or self.colour == "red" or self.colour == "red_amber"
        self.colour_state_index = {
            "green": 0,
            "amber": 1,
            "red": 2,
            "red_amber": 3
        }

        self.time_remaining = 0
        self.green_time = 0
        self.red_time = 0
        self.red_amber_time = 2
        self.amber_time = 3

    def get_state(self):
        return self.colour_state_index[self.colour]

    def set_state(self, colour: str):
        if colour == "green":
            if self.colour == "red":
                self.set_green()
        elif colour == "red":
            if self.colour == "green":
                self.set_red()

    def set_green(self):
        self.colour = "green"

        # if self.colour == "red":
        #     self.time_remaining = self.red_amber_time
        #     self.colour = "red_amber"

    def set_red(self):
        self.colour = "red"
        # if self.colour == "green":
        #     self.time_remaining = self.amber_time
        #     self.colour = "amber"

    def update(self, time_delta: float = 0.1) -> None:
        """

        :rtype: None
        :param time_delta: iteration length [s]
        """

        pass
        # if self.colour not in ["green", "red"]:
        #     self.time_remaining -= time_delta
        #     if self.time_remaining < 0:
        #         if self.colour == "amber":
        #             self.colour = "red"
        #             self.time_remaining = self.red_time
        #         elif self.colour == "red_amber":
        #             self.colour = "green"
        #             self.time_remaining = self.green_time

    def get_speed(self) -> float:
        return 0.0

    def get_length(self) -> float:
        return 0.0

    def allows_traffic(self) -> bool:
        if self.colour == "red" or self.colour == "amber":
            return False
        elif self.colour == "green":
            return True

    def get_time_remaining(self):
        return self.time_remaining