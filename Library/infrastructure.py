import random

from math import sin, cos, sqrt, floor
from numpy import polyfit, RankWarning
import warnings


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

        self.recalculate_coefs()

    def recalculate_coefs(self):
        self.calculate_spline_coefficients()
        self.calculate_poly_coefficients(self.poly_order)
        self.calculate_curvature()

    def get_distance(self):
        return sqrt((self.start_node.x - self.end_node.x) ** 2 + (self.start_node.y - self.end_node.y) ** 2)

    def calculate_spline_coefficients(self):
        _p1x = self.start_node.x
        _p1y = self.start_node.y
        _p1tx, _p1ty = self.start_node.get_tangents(self.get_distance() * 1.5)
        _p2x = self.end_node.x
        _p2y = self.end_node.y
        _p2tx, _p2ty = self.end_node.get_tangents(self.get_distance() * 1.5)
        _p2tx = -_p2tx
        _p2ty = -_p2ty
        self.x_hermite_cubic_coeff = [_p1x, _p1tx, -3 * _p1x + 3 * _p2x - 2 * _p1tx + _p2tx, 2 * _p1x - 2 * _p2x + _p1tx - _p2tx]
        self.y_hermite_cubic_coeff = [_p1y, _p1ty, -3 * _p1y + 3 * _p2y - 2 * _p1ty + _p2ty, 2 * _p1y - 2 * _p2y + _p1ty - _p2ty]

    def calculate_poly_coefficients(self, _order):
        warnings.simplefilter('ignore', RankWarning)
        if self.start_node.x == self.end_node.x:
            self.poly_coeff = self.start_node.x
        else:
            _x_array = []
            _y_array = []
            _path_length = round(self.get_distance() * 1.5)  # Changing iteration intervals for improved performance
            for i in range(_path_length + 1):
                s = i / _path_length
                _x_array.append(self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * s + self.x_hermite_cubic_coeff[2] * (s * s) + self.x_hermite_cubic_coeff[3] * (s * s * s))
                _y_array.append(self.y_hermite_cubic_coeff[0] + self.y_hermite_cubic_coeff[1] * s + self.y_hermite_cubic_coeff[2] * (s * s) + self.y_hermite_cubic_coeff[3] * (s * s * s))
            self.poly_coeff = list(polyfit(_x_array, _y_array, _order))

    def calculate_curvature(self):
        curvature = []
        if type(self.poly_coeff) is list:
            _path_length = round(
                self.get_distance() * 1.5)  # Changing iteration intervals for improved performance
            for _i in range(_path_length + 1):
                _s = _i / _path_length
                _x = self.x_hermite_cubic_coeff[0] + self.x_hermite_cubic_coeff[1] * _s + self.x_hermite_cubic_coeff[2] * (_s * _s) + self.x_hermite_cubic_coeff[3] * (_s * _s * _s)
                curvature.append(self.calculate_curve_radius(_x))

        _filter_size = 51
        _curvature = [0 for i in range(floor(_filter_size / 2))]
        for _rad_i in range(floor(_filter_size / 2), len(curvature) - floor(_filter_size / 2)):
            sum = 0
            for i in range(_filter_size):
                sum += curvature[_rad_i - floor(_filter_size / 2) + i]
            sum /= _filter_size
            _curvature.append(sum)
        _curvature += [0 for i in range(floor(_filter_size / 2))]
        self.curvature = _curvature

    def calculate_curve_radius(self, x):
        diff_1_coef = []
        diff_2_coef = []
        n_max = len(self.poly_coeff) - 1
        for n, coef in enumerate(self.poly_coeff):
            if n != n_max:
                diff_1_coef.append(coef * (n_max - n))
        for n, coef in enumerate(diff_1_coef):
            if n != n_max - 1:
                diff_2_coef.append(coef * (n_max - n - 1))
        y__ = 0
        for n, coef in enumerate(diff_2_coef):
            y__ += coef * pow(x, n_max - n - 2)
        y_ = 0
        for n, coef in enumerate(diff_1_coef):
            y_ += coef * pow(x, n_max - n - 1)
        k = abs(y__) / (pow((1 + (y_**2)), (3/2)))
        return k


class TrafficLight:
    def __init__(self, uid, paths: list = None, distance_traveled: float = 0.0, cycle_length: float = 10.0, cycle_red: float = 0.5,
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
