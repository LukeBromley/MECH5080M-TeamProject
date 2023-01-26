import random
from math import sin, cos, sqrt, floor, atan

import sympy as sym
from numpy import polyfit, RankWarning
import warnings

from Library.maths import Vector, calculate_cross_product, calculate_vector_magnitude


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
    def __init__(self, uid: int, start_node: Node, end_mode: Node, discrete_length_increment_size=0.01, discrete_iteration_qty=100000):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.x_hermite_cubic_coeff = []
        self.y_hermite_cubic_coeff = []

        self.discrete_length_increment_size = discrete_length_increment_size
        self.discrete_iteration_qty = discrete_iteration_qty
        self.discrete_path = []
        self.curvature = []

        self.calculate_all()

    # Gets
    def get_euclidean_distance(self):
        return sqrt((self.start_node.x - self.end_node.x) ** 2 + (self.start_node.y - self.end_node.y) ** 2)

    def get_s(self, arc_length: float):
        arc_length = round(arc_length * (1 / self.discrete_length_increment_size))
        return self.discrete_path[arc_length][0]

    def get_coords(self, arc_length: float):
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

    def calculate_all(self):
        self.calculate_hermite_spline_coefficients()
        self.calculate_discrete_arc_length_points()
        self.calculate_discrete_direction_points()
        self.calculate_discrete_curvature_points()

    def calculate_hermite_spline_coefficients(self):
        p1x = self.start_node.x
        p1y = self.start_node.y
        p1tx, p1ty = self.start_node.get_tangents(self.get_euclidean_distance() * 1.5)
        p2x = self.end_node.x
        p2y = self.end_node.y
        p2tx, p2ty = self.end_node.get_tangents(self.get_euclidean_distance() * 1.5)
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
            distance = sqrt((y1-y0)**2 + (x1-x0)**2)
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


class TrafficLight:
    def __init__(self, uid, paths: list = None, distance_traveled: float = 0.0, cycle_length: float = 10.0,
                 cycle_red: float = 0.5,
                 cycle_yellow: float = 0.4) -> None:
        """

        :param cycle_length: time it takes for the traffic light to complete a single light cycle [s]
        :param cycle_red: red state fraction of the cycle length
        :param cycle_yellow: yellow state fraction of the cycle length
        :param distance_traveled: position of the traffic light along the path [m]
        """

        self.uid = uid
        self.paths = paths if paths is not None else []
        self.distance_traveled = distance_traveled
        self.color = "green"
        self.cycle_time = 0.0
        self.cycle_red = cycle_red
        self.cycle_yellow = cycle_yellow
        self.cycle_length = cycle_length

    def update(self, time_delta: float = 0.1) -> None:
        """

        :rtype: None
        :param time_delta: iteration length [s]
        """

        self.cycle_time += time_delta
        if self.cycle_time < self.cycle_yellow * self.cycle_length:
            self.color = "green"
        elif self.cycle_time < self.cycle_red * self.cycle_length:
            self.color = "yellow"
        elif self.cycle_time < self.cycle_length:
            self.color = "red"
        else:
            self.cycle_time = 0.0

    def set_color(self, color: str) -> None:
        self.color = color

    def allows_traffic(self) -> bool:
        if self.color == "red":
            return False
        elif self.color == "green":
            return True
        elif self.color == "yellow":
            return random.random() > 0.5
