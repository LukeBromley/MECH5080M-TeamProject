import random
from math import sin, cos, sqrt, floor

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
    def __init__(self, uid: int, start_node: Node, end_mode: Node, poly_order=20):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.vehicles = []
        self.x_hermite_cubic_coeff = []
        self.y_hermite_cubic_coeff = []
        self.poly_order = poly_order
        self.poly_coeff = []
        self.curvature = []

        self._x = sym.Symbol('x')
        self._y = 0
        self.curvature_function = None
        self.arc_length_integrand = None
        self.second_order_diff = None
        self.first_order_diff = None

        self.recalculate_coefs()

    def recalculate_coefs(self):
        self.calculate_spline_coefficients()
        self.calculate_poly_coefficients()
        self.calculate_differentials()
        self.calculate_curvature_grid()

    def calculate_differentials(self):
        for order, coefficient in enumerate(reversed(self.poly_coeff)):
            self._y += coefficient * pow(sym.Symbol('x'), order)

        self.first_order_diff = sym.diff(self._y, self._x)
        self.second_order_diff = sym.diff(sym.diff(self._y, self._x), self._x)
        self.arc_length_integrand = sym.sqrt(1 + sym.diff(self._y, self._x) ** 2)
        self.curvature_function = abs(self.second_order_diff) / (1 + self.first_order_diff ** 2) ** 3 / 2

    def get_euclidean_distance(self):
        return sqrt((self.start_node.x - self.end_node.x) ** 2 + (self.start_node.y - self.end_node.y) ** 2)

    def calculate_spline_coefficients(self):
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

    def calculate_poly_coefficients(self):
        if self.start_node.x == self.end_node.x:
            self.poly_coeff = [self.start_node.x]
        else:
            x_array = []
            y_array = []
            path_length = round(self.get_euclidean_distance() * 1.5)
            for i in range(path_length + 1):
                s = i / path_length
                x_array.append(self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + self.x_hermite_cubic_coeff[2] * (s * s) + self.x_hermite_cubic_coeff[3] * (s * s * s))
                y_array.append(self.y_hermite_cubic_coeff[0] + self.y_hermite_cubic_coeff[1] * s + self.y_hermite_cubic_coeff[2] * (s * s) + self.y_hermite_cubic_coeff[3] * (s * s * s))

            good_poly_found = False
            while not good_poly_found and self.poly_order > 3:
                with warnings.catch_warnings():
                    warnings.filterwarnings('error')
                    try:
                        polynomial = polyfit(x_array, y_array, self.poly_order)
                        good_poly_found = True
                    except RankWarning:
                        self.poly_order -= 1

            self.poly_coeff = list(polynomial)
            
    def calculate_curvature_grid(self):
        curvature = []
        if type(self.poly_coeff) is list:
            path_length = round(self.get_euclidean_distance() * 1.5)
            for i in range(path_length + 1):
                s = i / path_length
                curvature.append(self.calculate_curvature(s))
        self.curvature = curvature

    def calculate_curvature(self, s: float):
        ## Source: https://math.libretexts.org/Bookshelves/Calculus/Supplemental_Modules_(Calculus)/Vector_Calculus/2%3A_Vector-Valued_Functions_and_Motion_in_Space/2.3%3A_Curvature_and_Normal_Vectors_of_a_Curve

        dy_ds = self.y_hermite_cubic_coeff[1] + 2 * self.y_hermite_cubic_coeff[2] * s + 3 * self.y_hermite_cubic_coeff[3] * s * s
        dy2_ds2 = 2 * self.y_hermite_cubic_coeff[2] + 6 * self.y_hermite_cubic_coeff[3] * s

        dx_ds = self.x_hermite_cubic_coeff[1] + 2 * self.x_hermite_cubic_coeff[2] * s + 3 * self.x_hermite_cubic_coeff[3] * (s * s)
        dx2_ds2 = 2 * self.x_hermite_cubic_coeff[2] + 6 * self.x_hermite_cubic_coeff[3] * s

        dR_ds = Vector(dx_ds, dy_ds, 0)
        dR2_ds2 = Vector(dx2_ds2, dy2_ds2, 0)

        return calculate_vector_magnitude(calculate_cross_product(dR_ds, dR2_ds2)) / (calculate_vector_magnitude(dR_ds)**3)

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
