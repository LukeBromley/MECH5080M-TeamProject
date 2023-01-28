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
        self.model.get_lights()[0].set_state("red")
        self.model.get_lights()[1].set_state("green")

        dt = 0.01
        while True:
            if random.random() > 0.995:
                self.add_vehicle(random.choice([1, 2]))

            for light in self.model.get_lights():
                light.update(dt)

            coordinates = []
            for vehicle in self.model.get_vehicles():
                route = self.model.get_route(vehicle.route_uid)
                coordinates.append(route.get_coordinates(vehicle.get_route_distance_travelled()))
                object_ahead = self.get_object_ahead(vehicle.uid)
                vehicle.update(dt, object_ahead)
                vehicle.update_position_data(coordinates[-1])

            self.visualiser.update_vehicle_positions(coordinates)
            self.time += dt
            sleep(dt)

    def get_object_ahead(self, vehicle_uid):
        path_object_ahead = self.get_path_object_ahead(vehicle_uid)
        if path_object_ahead is not None:
            return path_object_ahead
        else:
            return self.get_route_object_ahead(vehicle_uid)

    def get_path_object_ahead(self, vehicle_uid):
        object_ahead = None
        path_minimum_distance_ahead = float('inf')

        this_vehicle = self.model.get_vehicle(vehicle_uid)
        this_route = self.model.get_route(this_vehicle.route_uid)
        this_path, this_index = this_route.get_path_and_index(this_vehicle.get_route_distance_travelled())

        for vehicle in self.model.get_vehicles():
            that_path, that_index = self.model.get_route(vehicle.route_uid).get_path_and_index(vehicle.get_route_distance_travelled())
            if (
                    this_path == that_path and
                    this_index < that_index and
                    that_index - this_index < path_minimum_distance_ahead
            ):
                path_minimum_distance_ahead = that_index - this_index
                object_ahead = vehicle
        return object_ahead

    def get_route_object_ahead(self, vehicle_uid):
        object_ahead = None
        path_minimum_distance_ahead = float('inf')

        this_vehicle = self.model.get_vehicle(vehicle_uid)
        this_route = self.model.get_route(this_vehicle.route_uid)
        this_vehicle_path, _ = this_route.get_path_and_index(this_vehicle.get_route_distance_travelled())
        this_vehicle_path_uid = this_vehicle_path.uid

        this_route_distance_traveled = this_vehicle.get_route_distance_travelled()
        this_route_path_uids = self.model.get_route(this_vehicle.route_uid).get_path_uids()

        for light in self.model.get_lights():
            path_uids_ahead = this_route_path_uids[this_route_path_uids.index(this_vehicle_path_uid) + 1:]
            if light.path_uid in path_uids_ahead and not light.allows_traffic():
                path_minimum_distance_ahead = this_route.get_route_distance_travelled_to_path(light.path_uid) - this_route_distance_traveled
                light.set_route_distance_travelled(this_route.get_route_distance_travelled_to_path(light.path_uid))
                object_ahead = light

        for vehicle in self.model.get_vehicles():
            if (
                    this_vehicle.route_uid == vehicle.route_uid and
                    this_route_distance_traveled < vehicle.get_route_distance_travelled() and
                    vehicle.get_route_distance_travelled() - this_route_distance_traveled < path_minimum_distance_ahead
            ):
                path_minimum_distance_ahead = vehicle.get_route_distance_travelled() - this_route_distance_traveled
                object_ahead = vehicle
        return object_ahead

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route_uid: int):
        self.uid += 1
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.time,
                route_uid=route_uid,
                velocity=10.0,
                acceleration=0.0,
                maximum_acceleration=4.0,
                maximum_deceleration=7.0,
                preferred_time_gap=2.0,
                vehicle_length=2.0,
                maximum_velocity=30.0
            )
        )

if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"))
    sim.run()

