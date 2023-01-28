from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.infrastructure import Route
from Library.model import Model
from Library.vehicles import Vehicle
from config import ROOT_DIR
import os
import random
from functools import partial

class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0
        self.uid = 0

        self.model = Model()
        self.model.load_junction(file_path)

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

    def main(self):
        dt = 0.01
        while True:
            if random.random() > 0.99:
                self.add_vehicle(random.choice([1, 2]))
            coordinates = []
            for vehicle in self.model.get_vehicles():
                route = self.model.get_route(vehicle.route_uid)
                coordinates.append(route.get_coordinates(vehicle.get_route_distance_travelled()))
                object_ahead = self.get_object_ahead(vehicle.uid)
                vehicle.update(dt, object_ahead)
                vehicle.update_position_data(coordinates[-1])

            self.visualiser.update_vehicle_positions(coordinates)
            self.time += dt
            sleep(0.01)

    def get_object_ahead(self, vehicle_uid):
        path_vehicle_ahead = None
        this_vehicle = self.model.get_vehicle(vehicle_uid)
        this_route_distance_traveled = this_vehicle.get_route_distance_travelled()
        route = self.model.get_route(this_vehicle.route_uid)

        vehicles = self.model.get_vehicles()
        # TODO: Check for lights after vehicles
        lights = self.model.get_lights()
        if vehicles is None and lights is None:
            return
        this_path, this_index = route.get_path_and_index(this_route_distance_traveled)

        path_minimum_distance_ahead = float('inf')
        for vehicle in vehicles:
            that_path, that_index = self.model.get_route(vehicle.route_uid).get_path_and_index(vehicle.get_route_distance_travelled())
            if (
                    this_path == that_path and
                    this_index < that_index and
                    that_index - this_index < path_minimum_distance_ahead
            ):
                path_minimum_distance_ahead = that_index - this_index
                path_vehicle_ahead = vehicle

        if path_vehicle_ahead is not None:
            return path_vehicle_ahead

        path_minimum_distance_ahead = float('inf')
        for vehicle in vehicles:
            if (
                    self.uid == vehicle.route_uid and
                    this_route_distance_traveled < vehicle.get_route_distance_travelled() and
                    vehicle.get_route_distance_travelled() - this_route_distance_traveled < path_minimum_distance_ahead
            ):
                path_minimum_distance_ahead = vehicle.get_route_distance_travelled() - this_route_distance_traveled
                path_vehicle_ahead = vehicle

        if path_vehicle_ahead is not None:
            return path_vehicle_ahead

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route_uid: int):
        self.uid += 1
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.time,
                route_uid=route_uid,
                velocity=15.0,
                acceleration=0.0,
                maximum_acceleration=3.0,
                maximum_deceleration=6.0,
                preferred_time_gap=2.0,
                vehicle_length=4.0,
                maximum_velocity=30.0
            )
        )

if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"))
    sim.run()

