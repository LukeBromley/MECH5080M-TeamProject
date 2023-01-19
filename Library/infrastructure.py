import random

import sympy

from math import sin, cos


class Node:
    def __init__(self, uid: int, x: float, y: float, angle=None):
        self.uid = uid
        self.x = x
        self.y = y
        self.angle = angle
        temp = 1

    def get_tangents(self, _weight=None):
        tx = _weight * sin(self.angle)
        ty = -_weight * cos(self.angle)
        return tx, ty

class Path:
    def __init__(self, uid: int, start_node: Node, end_mode: Node, coeffs: tuple):
        self.uid = uid
        self.start_node = start_node
        self.end_node = end_mode
        self.vehicles = []
        self.x_coeff, self.y_coeff = coeffs[0], coeffs[1]

class TrafficLight:
    def __init__(self, path: Path, distance_traveled: float = 0.0, cycle_length: float = 10.0, cycle_red: float = 0.5,
                 cycle_yellow: float = 0.4) -> None:
        """

        :param cycle_length: time it takes for the traffic light to complete a single light cycle [s]
        :param cycle_red: red state fraction of the cycle length
        :param cycle_yellow: yellow state fraction of the cycle length
        :param distance_traveled: position of the traffic light along the path [m]
        """

        self.path = path
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
