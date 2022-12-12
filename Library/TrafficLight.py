from typing import List
import random
import matplotlib.pyplot as plt
import numpy as np


class TrafficLight:
    def __init__(self, cycle_length: float = 10.0, cycle_red: float = 0.5, cycle_yellow: float = 0.4,
                 position_longitudinal: float = 0.0, position_lateral: float = 0.0) -> None:
        """

        :param cycle_length: time it takes for the traffic light to complete full light cycle [s]
        :param cycle_red: red state fraction of the cycle length
        :param cycle_yellow: yellow state fraction of the cycle length
        :param position_longitudinal: longitudinal position of the traffic light along the road [m]
        :param position_lateral: lateral position of the traffic perpendicular to the road [m]
        """

        self.color = "green"
        self.cycle_time = 0.0
        self.cycle_red = cycle_red
        self.cycle_yellow = cycle_yellow
        self.cycle_length = cycle_length
        self.position_longitudinal = position_longitudinal

    def update(self, time_delta: float = 1.0) -> None:
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

