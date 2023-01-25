import random
from math import sin, cos, sqrt, atan

import sympy as sym
from numpy import polyfit, RankWarning
import warnings

# https://fjorgedigital.com/insights/blog/can-bezier-curves-be-quickly-parameterized-by-arc-length/


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
    def __init__(self, uid: int, start_node: Node, end_mode: Node):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.vehicles = []

        self.x_hermite_cubic_coeff = []
        self.y_hermite_cubic_coeff = []

        self.points_data = []
        self.length_unit_size = 1
        self.length_unit_error = 0.001

        self.recalculate_coefs()

    # Stat Get Functions
    def get_coords_by_s_terms(self, s):
        x = self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + self.x_hermite_cubic_coeff[2] * (s * s) + self.x_hermite_cubic_coeff[3] * (s * s * s)
        y = self.y_hermite_cubic_coeff[0] + self.y_hermite_cubic_coeff[1] * s + self.y_hermite_cubic_coeff[2] * (s * s) + self.y_hermite_cubic_coeff[3] * (s * s * s)
        return x, y

    def get_euclidean_distance(self):
        return sqrt((self.start_node.x - self.end_node.x) ** 2 + (self.start_node.y - self.end_node.y) ** 2)

    def get_coords_from_arc_length(self, length: int):
        x = self.points_data[length][0]
        y = self.points_data[length][1]
        return x, y

    def get_angle_from_arc_length(self, length: int):
        if 0 < length < len(self.points_data) - 1:
            dx = self.points_data[length + 1][0] - self.points_data[length - 1][0]
            dy = self.points_data[length + 1][1] - self.points_data[length - 1][1]
            angle = atan(dy / dx)
            return angle
        elif length == 0:
            dx = self.points_data[3][0] - self.points_data[0][0]
            dy = self.points_data[3][1] - self.points_data[0][1]
            angle = atan(dy / dx)
            return angle
        elif length == len(self.points_data) - 1:
            dx = self.points_data[len(self.points_data) - 1][0] - self.points_data[len(self.points_data) - 3][0]
            dy = self.points_data[len(self.points_data) - 1][1] - self.points_data[len(self.points_data) - 3][1]
            angle = atan(dy / dx)
            return angle

    def get_curvature_from_arc_length(self, length: int):
        """

        Curvature = dθ/ds = 2π/2πR
        :param length:
        :return:
        """
        if 0 < length < len(self.points_data):
            dx = self.points_data[length][0] - self.points_data[length - 1][0]
            dy = self.points_data[length][1] - self.points_data[length - 1][1]
            curvature = atan(dy / dx)
            return curvature

    # Calculations
    def recalculate_coefs(self):
        self.calculate_hermite_spline_coefficients()
        self.calculate_arc_length_points()
        # self.calculate_differentials()
        # self.calculate_curvature_grid()

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
            
    def calculate_arc_length_points(self):
        number_of_iterations = 10000

        x_start, y_start = self.get_coords_by_s_terms(0)
        self.points_data = [[x_start, y_start]]
        for iteration in range(1, number_of_iterations + 1):
            s = iteration / number_of_iterations
            x1, y1 = self.get_coords_by_s_terms(s)

            x0 = self.points_data[-1][0]
            y0 = self.points_data[-1][1]
            distance = sqrt((y1-y0)**2 + (x1-x0)**2)
            distance_delta = self.length_unit_size - distance
            if abs(distance_delta) < self.length_unit_error:
                self.points_data.append([x1, y1])


    # def calculate_differentials(self):
    #     for order, coefficient in enumerate(reversed(self.poly_coeff)):
    #         self._y += coefficient * pow(sym.Symbol('x'), order)
    #
    #     self.first_order_diff = sym.diff(self._y, self._x)
    #     self.second_order_diff = sym.diff(sym.diff(self._y, self._x), self._x)
    #     self.arc_length_integrand = sym.sqrt(1 + sym.diff(self._y, self._x) ** 2)
    #     self.curvature_function = abs(self.second_order_diff) / (1 + self.first_order_diff ** 2) ** 3 / 2
    #
    # def calculate_curvature_grid(self):
    #     curvature = []
    #     if type(self.poly_coeff) is list:
    #         path_length = round(
    #             self.get_euclidean_distance() * 1.5)
    #         for i in range(path_length + 1):
    #             s = i / path_length
    #             x = self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + self.x_hermite_cubic_coeff[
    #                 2] * (s * s) + self.x_hermite_cubic_coeff[3] * (s * s * s)
    #             curvature.append(self.calculate_curvature(x))
    #
    #     filter_size = 51
    #     filtered_curvature = [0 for i in range(floor(filter_size / 2))]
    #     for rad_i in range(floor(filter_size / 2), len(curvature) - floor(filter_size / 2)):
    #         sum = 0
    #         for i in range(filter_size):
    #             sum += curvature[rad_i - floor(filter_size / 2) + i]
    #         sum /= filter_size
    #         filtered_curvature.append(sum)
    #     filtered_curvature += [0 for i in range(floor(filter_size / 2))]
    #     self.curvature = filtered_curvature
    #
    # def calculate_curvature(self, x):
    #     diff_1_coef = []
    #     diff_2_coef = []
    #     n_max = len(self.poly_coeff) - 1
    #     for n, coef in enumerate(self.poly_coeff):
    #         if n != n_max:
    #             diff_1_coef.append(coef * (n_max - n))
    #     for n, coef in enumerate(diff_1_coef):
    #         if n != n_max - 1:
    #             diff_2_coef.append(coef * (n_max - n - 1))
    #     y__ = 0
    #     for n, coef in enumerate(diff_2_coef):
    #         y__ += coef * pow(x, n_max - n - 2)
    #     y_ = 0
    #     for n, coef in enumerate(diff_1_coef):
    #         y_ += coef * pow(x, n_max - n - 1)
    #     return abs(y__) / (pow((1 + (y_ ** 2)), (3 / 2)))
    #
    # def calculate_distance_traveled(self, a: float, b: float, n: int = 10):
    #     x = sym.Symbol('x')
    #     h = (b - a) / n
    #     distance_traveled = 0
    #     for i in range(1, int(n / 2 + 1), 1):
    #         distance_traveled += (
    #                 self.arc_length_integrand.subs(x, a + (2 * i - 2) * h) +
    #                 4 * self.arc_length_integrand.subs(x, a + (2 * i - 1) * h) +
    #                 self.arc_length_integrand.subs(x, a + (2 * i) * h)
    #         )
    #     return h * distance_traveled / 3
    #
    # def get_coordinates(self, distance_traveled: float, n: int = 100):
    #     # The arc length integral is non-convergent.
    #
    #     a = self.start_node.x
    #     b = self.end_node.x
    #     x = sym.Symbol('x')
    #     h = (b - a) / n
    #     distance = 0
    #     for i in range(1, int(n / 2 + 1), 1):
    #         distance += (
    #                 self.arc_length_integrand.subs(x, a + (2 * i - 2) * h) +
    #                 4 * self.arc_length_integrand.subs(x, a + (2 * i - 1) * h) +
    #                 self.arc_length_integrand.subs(x, a + (2 * i) * h)
    #         )
    #         if h * distance / 3 > distance_traveled:
    #             x_i = a + 2*i*h
    #             return x_i, self._y.subs(x, x_i)
    #         elif i >= int(n / 2):
    #             return self.end_node.x, self.end_node.y

    # Vehicle
    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def get_vehicle_ahead(self, distance_traveled: float):
        distances_traveled = [vehicle.get_distance_traveled() for vehicle in self.vehicles]
        greater_distances_traveled = [i for i in distances_traveled if distance_traveled < i]

        if greater_distances_traveled:
            closes_distance_traveled = min(greater_distances_traveled)
            return self.vehicles[distances_traveled.index(closes_distance_traveled)]


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
