from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
#from Library.infrastructure import Route
from Library.model import Model
from Library.vehicles import Vehicle, GhostVehicle
from Library.environment import Spawning, Time
from config import ROOT_DIR
import os
#import random
#from functools import partial
#import matplotlib.pyplot as plt



class Simulation:
    def __init__(self, file_path: str):
        self.time = 0.0
        self.uid = 0

        self.model = Model()
        self.model.load_junction(file_path)

        self.model.set_start_time_of_day(Time(12, 0, 0))
        self.model.set_tick_rate(100)

        self.visualiser = JunctionVisualiser()
        self.visualiser.define_main(self.main)
        self.visualiser.load_junction(file_path)
        self.visualiser.set_scale(50)

        self.spawning = []

        for node_uid in self.model.calculate_start_nodes():
            self.spawning.append(Spawning(node_uid, self.model.start_time_of_day))

    def main(self):

        ghost_vehicles = []

        for i in range(8640000):
            time = self.model.calculate_time_of_day()

            if i % 200 == 0:
                self.add_vehicle(2)

            # if i % 75 == 0:
            #     self.add_vehicle(1)

            coordinates = []
            self.model.remove_finished_vehicles()
            for index, vehicle in enumerate(self.model.vehicles):

                coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
                angle = self.model.get_angle(vehicle.uid)

                if time.total_seconds() % 3 == 0:

                    old_path_uid = self.model.get_vehicle_path_uid(vehicle.uid)
                    old_path = self.model.get_path(old_path_uid)
                    s = old_path.get_s(vehicle.get_path_distance_travelled())

                    ghost_vehicles.append(GhostVehicle(vehicle.uid, old_path_uid, time))

                    if vehicle.route_uid == 2:
                        vehicle.route_uid = 1

                    new_path_uid = self.model.get_vehicle_path_uid(vehicle.uid)
                    new_path = self.model.get_path(new_path_uid)
                    arc_length = new_path.get_arc_length_from_s(s)
                    if arc_length is None:
                        print(1)
                    vehicle.set_distance_travelled(arc_length)

                # ghost_vehicles_to_remove = []
                # for ghost_vehicle in ghost_vehicles:
                #     t_delta = time.total_milliseconds() - ghost_vehicle.time_created.total_milliseconds()
                #     if t_delta < 2000:
                #         new_path = self.model.get_path(self.model.get_vehicle_path_uid(ghost_vehicle.parent_vehicle_uid))
                #         s = new_path.get_s(vehicle.get_path_distance_travelled())
                #         old_path = self.model.get_path(ghost_vehicle.path_uid)
                #         arc_length = old_path.get_arc_length_from_s(s)
                #
                #         from_x, from_y = old_path.get_coordinates(arc_length)
                #         to_x, to_y = self.model.get_vehicle_coordinates(ghost_vehicle.parent_vehicle_uid)
                #
                #         # x = t_delta * (to_x - from_x) / 2000
                #         # y = t_delta * (to_y - from_y) / 2000
                #
                #         # old_x -= (time.total_milliseconds() - ghost_vehicle.time_created.total_milliseconds()) * 0.01
                #         coordinates.append([from_x, from_y, angle])
                #     else:
                #         ghost_vehicles_to_remove.append(ghost_vehicle.parent_vehicle_uid)
                #
                # for ghost_vehicle_to_remove in ghost_vehicles_to_remove:
                #     for index, ghost_vehicle in enumerate(ghost_vehicles):
                #         if ghost_vehicle.parent_vehicle_uid == ghost_vehicle_to_remove:
                #             ghost_vehicles.pop(index)
                #             break

                coordinates.append([coord_x, coord_y, angle])
                object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)

                vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead)
                # vehicle.update_position_data(coordinates[-1][:2])

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
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "Lane_Changing_2.junc"))
    sim.run()
