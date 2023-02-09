from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.model import Model
from Library.vehicles import Vehicle, GhostVehicle
from Library.environment import Spawning, Time
from Library.maths import calculate_rectangle_corner_coords, calculate_range_overlap, calculate_line_gradient_and_constant
from config import ROOT_DIR
import os
from copy import deepcopy as copy
from math import cos, sin, atan2, pi

import matplotlib as plt


class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0
        self.uid = 0

        # Model
        self.model = Model()
        self.model.load_junction(file_path)
        self.model.generate_routes()

        # Time
        self.model.set_start_time_of_day(Time(12, 0, 0))
        self.model.set_tick_rate(100)

        # Visualiser
        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

        # Spawning system
        self.spawning = []
        for node_uid in self.model.calculate_start_nodes():
            self.spawning.append(Spawning(node_uid, self.model.start_time_of_day))

        self.ghost_vehicles = []

    def main(self):
        #for route in self.model.routes:
            #print("Route_uid =", route.uid)
            #print("\nPaths =", route.get_path_uids())
            #print("\n\n")
        for i in range(8640000):  # 24 simulation hours

            # Current Time
            time = self.model.calculate_time_of_day()
            if i % 90000 == 0:
                # print the time every 15 simulation mins
                print(time)

            time = self.model.calculate_time_of_day()
            for index, node_uid in enumerate(self.model.calculate_start_nodes()):
                if self.spawning[index].nudge(time):
                    route_uid = self.spawning[index].select_route(self.model.get_routes_with_starting_node(node_uid))
                    self.add_vehicle(route_uid, 2, 2)

            # Remove finished vehicles
            self.remove_finished_vehicles()

            # Update vehicle position
            coordinates_angle_size = []

            for vehicle in self.model.vehicles:
                coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
                angle = self.model.get_vehicle_direction(vehicle.uid)

                if vehicle.get_path_distance_travelled() > 0 and not vehicle.changing_lane:
                    if self.model.is_lane_change_required(vehicle.uid):
                        self.model.change_vehicle_lane(vehicle.uid, time)

                object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
                vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
                vehicle.update_position_data([coord_x, coord_y])

                if vehicle.uid in [ghost.uid for ghost in self.model.ghost_vehicles]:
                    coordinates_angle_size.append([coord_x, coord_y])
                else:
                    coordinates_angle_size.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])
            if self.model.ghost_vehicles:
                self.model.remove_ghosts(time, coordinates_angle_size)
            
            # Update visualiser
            self.visualiser.update_vehicle_positions(coordinates_angle_size)
            self.visualiser.update_light_colours(self.model.lights)
            self.visualiser.update_time(self.model.calculate_time_of_day())

            # Increment Time
            self.model.tock()
            sleep((self.model.tick_time)/5)

    def run(self):
        self.visualiser.open()

    def add_vehicle(self, route_uid: int, length, width):
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
                length=length,
                width=width
            )
        )

    def remove_finished_vehicles(self):
        vehicle_uids_removed = self.model.remove_finished_vehicles()
        for uid in vehicle_uids_removed:
            for index, ghost_vehicles in enumerate(self.ghost_vehicles):
                if ghost_vehicles.uid == uid:
                    self.ghost_vehicles.pop(index)
                    break


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "example_junction_with_lanes.junc"))
    sim.run()
