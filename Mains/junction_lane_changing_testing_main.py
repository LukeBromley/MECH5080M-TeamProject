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
        for i in range(8640000):  # 24 simulation hours

            # Current Time
            time = self.model.calculate_time_of_day()
            if i % 90000 == 0:
                # print the time every 15 simulation mins
                print(time)

            if i % 200 == 0:
                self.add_vehicle(2, 3, 2)

            # Remove finished vehicles
            self.remove_finished_vehicles()

            # Update vehicle position
            coordinates_angle_size = []

            for vehicle in self.model.vehicles:
                coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
                angle = self.model.get_angle(vehicle.uid)

                if time.total_seconds() % 3 == 0:

                    if vehicle.route_uid == 2:
                        old_path_uid = self.model.get_vehicle_path_uid(vehicle.uid)
                        old_path = self.model.get_path(old_path_uid)
                        s = old_path.get_s(vehicle.get_path_distance_travelled())

                        self.ghost_vehicles.append(GhostVehicle(vehicle.uid, old_path_uid, time))

                        vehicle.route_uid = 1

                        new_path_uid = self.model.get_vehicle_path_uid(vehicle.uid)
                        new_path = self.model.get_path(new_path_uid)
                        arc_length = new_path.get_arc_length_from_s(s)
                        vehicle.set_distance_travelled(arc_length)

                object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
                vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
                vehicle.update_position_data([coord_x, coord_y])

                if vehicle.uid in [ghost.uid for ghost in self.ghost_vehicles]:
                    coordinates_angle_size.append([coord_x, coord_y])
                else:
                    coordinates_angle_size.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])

            ghost_vehicle_uids_to_remove = []
            for ghost_vehicle in self.ghost_vehicles:
                t_delta = time.total_milliseconds() - ghost_vehicle.time_created.total_milliseconds()
                if t_delta < 2000:
                    new_path = self.model.get_path(self.model.get_vehicle_path_uid(ghost_vehicle.uid))
                    vehicle = self.model.get_vehicle(ghost_vehicle.uid)
                    s = new_path.get_s(vehicle.get_path_distance_travelled())
                    old_path = self.model.get_path(ghost_vehicle.path_uid)
                    from_x, from_y = old_path.get_coordinates_from_s(s)
                    to_x, to_y = self.model.get_vehicle_coordinates(ghost_vehicle.uid)
                    angle = self.model.get_angle(ghost_vehicle.uid)

                    x = (t_delta / 2000) * (to_x - from_x) + from_x
                    y = (t_delta / 2000) * (to_y - from_y) + from_y

                    coordinates_angle_size.append([x, y, angle, vehicle.length, vehicle.width, vehicle.uid])
                else:
                    ghost_vehicle_uids_to_remove.append(ghost_vehicle.uid)

            for ghost_vehicle_uid in ghost_vehicle_uids_to_remove:
                for index, ghost_vehicle in enumerate(self.ghost_vehicles):
                    if ghost_vehicle.uid == ghost_vehicle_uid:
                        self.ghost_vehicles.pop(index)
                        break

            # Update visualiser
            self.visualiser.update_vehicle_positions(coordinates_angle_size)
            self.visualiser.update_light_colours(self.model.lights)
            self.visualiser.update_time(self.model.calculate_time_of_day())

            # Increment Time
            self.model.tock()
            sleep(self.model.tick_time)

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
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "Lane_Changing_2.junc"))
    sim.run()
