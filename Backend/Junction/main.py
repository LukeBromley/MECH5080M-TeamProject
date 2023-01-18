import math
import os

import numpy as np
import sympy as sym
from matplotlib import pyplot as plt

from Frontend.JunctionFileManagement import JunctionFileManagement
from Library.vehicles import Car
from config import ROOT_DIR


class Simulation:
    def __init__(self, file_path: str):
        self.nodes, self.paths, self.lights = JunctionFileManagement().load_from_file(file_path)
        car = Car(
            path=self.paths[1],
            velocity=0.0,
            acceleration=0.0,
            maximum_acceleration=5.0,
            maximum_deceleration=4.0,
            distance_traveled=0,
            preferred_time_gap=2.0,
            vehicle_length=4.0
        )
        self.vehicles = [car]

    def update(self, dt: float = 1/30):
        for car in self.vehicles:
            car.update(dt)

    def get_vehicles(self):
        return self.vehicles

if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "Example_Junction_With_Lights.junc"))

    plt.ion()
    fig, ax = plt.subplots()
    scatter = ax.scatter([], [])
    ax.set_xlim(-200, 200)
    ax.set_ylim(-200, 200)

    for x in range(1000):
        car = sim.get_vehicles()[0]
        sim.update(0.1)

        scatter.set_offsets(np.c_[car.get_cartesian_position()])
        fig.canvas.draw_idle()
        plt.pause(0.1)


