from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.infrastructure import Route
from Library.model import Model
from Library.vehicles import Vehicle
from Library.environment import Spawning, Time
from config import ROOT_DIR
import os
import random
from functools import partial
import matplotlib.pyplot as plt


class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0
        self.uid = 0

        self.model = Model()
        self.model.load_junction(file_path)

        self.model.set_start_time_of_day(Time(8, 0, 0))
        self.model.set_tick_rate(100)

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

        self.spawning = []

        for node_uid in self.model.calculate_start_nodes():
            self.spawning.append(Spawning(node_uid, self.model.start_time_of_day))

    def main(self):
        for i in range(8640000):

            time = self.model.calculate_time_of_day()
            for index, node_uid in enumerate(self.model.calculate_start_nodes()):
                if self.spawning[index].nudge(time):
                    route_uid = self.spawning[index].select_route(self.model.get_routes_with_starting_node(node_uid))
                    self.add_vehicle(route_uid)

            for light in self.model.get_lights():
                light.update(self.model.tick_time)

            coordinates = []
            for vehicle in self.model.get_vehicles():
                vehicle_uid = vehicle.uid
                coordinates.append(self.model.get_coordinates_on_path(vehicle_uid))

                object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle_uid)
                vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
                vehicle.update_position_data(coordinates[-1])

            self.visualiser.update_vehicle_positions(coordinates)
            self.visualiser.update_light_colours(self.model.lights)
            self.model.tock()
            sleep(self.model.tick_time)
            if i % 90000 == 0:
                print(self.model.calculate_time_of_day())

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route_uid: int):
        self.uid += 1
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.time,
                route_uid=route_uid,
                velocity=5.0,
                acceleration=0.0,
                maximum_acceleration=3.0,
                maximum_deceleration=9.0,
                preferred_time_gap=2.0,
                maximum_velocity=30.0,
                length=2.5
            )
        )


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"))
    sim.run()
