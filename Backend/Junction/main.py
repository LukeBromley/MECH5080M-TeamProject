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

        for path in self.paths:
            path.add_vehicle(
                Car(
                    path=path,
                    velocity=20.0,
                    acceleration=0.0,
                    maximum_acceleration=5.0,
                    maximum_deceleration=4.0,
                    distance_traveled=0,
                    preferred_time_gap=2.0,
                    vehicle_length=4.0,
                    maximum_velocity=30.0
                )
            )
            path.add_vehicle(
                Car(
                    path=path,
                    velocity=0.0,
                    acceleration=0.0,
                    maximum_acceleration=5.0,
                    maximum_deceleration=4.0,
                    distance_traveled=60.0,
                    preferred_time_gap=2.0,
                    vehicle_length=4.0,
                    maximum_velocity=30.0
                )
            )

    def update(self, dt: float = 1 / 30):
        for path in self.paths:
            for car in path.vehicles:
                car.update(dt)


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "Example_Junction_With_Lights.junc"))

    plt.ion()
    fig, ax = plt.subplots()
    for node in sim.nodes:
        ax.scatter(node.x, node.y, c='dimgray', s=70, marker='s')
    scatter = ax.scatter([], [], c='lightseagreen')

    dt = 0.1
    for x in range(1000):
        sim.update(dt)
        ax.set_title(f"t = {round(x * dt, 1)}")

        coordinates_x = []
        coordinates_y = []
        for path in sim.paths:
            for car in path.vehicles:
                cartesian_coordinates = car.get_cartesian_position()
                coordinates_x.append(cartesian_coordinates[0])
                coordinates_y.append(cartesian_coordinates[1])

        scatter.set_offsets(np.c_[coordinates_x, coordinates_y])
        fig.canvas.draw_idle()
        plt.pause(0.001)
