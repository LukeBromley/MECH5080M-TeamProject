from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

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
        self.model.generate_routes()

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

    def main(self):
        dt = 0.01
        while True:
            if random.random() > 0.995:
                self.add_vehicle(random.choice(self.model.get_route_uids()))

            for light in self.model.get_lights():
                light.update(dt)

            coordinates = []
            for vehicle in self.model.get_vehicles():
                route = self.model.get_route(vehicle.route_uid)
                coordinates.append(route.get_coordinates(vehicle.get_route_distance_travelled()))

                object_ahead, delta_distance_ahead = self.get_object_ahead(vehicle.uid)
                vehicle.update(dt, object_ahead, delta_distance_ahead)
                vehicle.update_position_data(coordinates[-1])

            self.visualiser.update_vehicle_positions(coordinates)
            self.time += dt
            sleep(dt)

    def get_object_ahead(self, vehicle_uid):
        object_ahead = None

        this_vehicle = self.model.get_vehicle(vehicle_uid)
        this_route = self.model.get_route(this_vehicle.route_uid)
        this_path, this_vehicle_path_distance_travelled = this_route.get_path_and_path_distance_travelled(this_vehicle.get_route_distance_travelled())

        # Search the current path
        min_path_distance_travelled = float('inf')
        for that_vehicle in self.model.get_vehicles():
            that_path, that_vehicle_path_distance_travelled = self.model.get_route(that_vehicle.route_uid).get_path_and_path_distance_travelled(that_vehicle.get_route_distance_travelled())
            if that_path.uid == this_path.uid and min_path_distance_travelled > that_vehicle_path_distance_travelled > this_vehicle_path_distance_travelled:
                min_path_distance_travelled = that_vehicle_path_distance_travelled
                object_ahead = that_vehicle

        if object_ahead is not None:
            return object_ahead, min_path_distance_travelled - this_vehicle_path_distance_travelled

        # Search the paths ahead
        this_route_path_uids = self.model.get_route(this_vehicle.route_uid).get_path_uids()
        path_uids_ahead = this_route_path_uids[this_route_path_uids.index(this_path.uid) + 1:]
        distance_travelled_offset = this_path.get_length() - this_vehicle_path_distance_travelled
        for path_uid in path_uids_ahead:
            for light in self.model.get_lights():
                if light.path_uid == path_uid and not light.allows_traffic():
                    return light, distance_travelled_offset
            for that_vehicle in self.model.get_vehicles():
                that_path, that_vehicle_path_distance_travelled = self.model.get_route(that_vehicle.route_uid).get_path_and_path_distance_travelled(that_vehicle.get_route_distance_travelled())
                if that_path.uid == path_uid and min_path_distance_travelled > that_vehicle_path_distance_travelled:
                    min_path_distance_travelled = that_vehicle_path_distance_travelled
                    object_ahead = that_vehicle

            if object_ahead is not None:
                return object_ahead, min_path_distance_travelled + distance_travelled_offset
            else:
                distance_travelled_offset += self.model.get_path(path_uid).get_length()
                continue

        return None, None

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
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "Roundabout3.junc"))
    sim.run()
