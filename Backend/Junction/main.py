import random
from platform import system

import numpy as np
from numpy import mean

from Library.maths import calculate_range_overlap, calculate_line_gradient_and_constant, \
    calculate_rectangle_corner_coords
import sys

if system() == 'Windows':
    sys.path.append('./')

from time import sleep
from Frontend.JunctionVisualiser import JunctionVisualiser
from Library.model import Model
from Library.vehicles import Vehicle
from Library.environment import SpawningRandom, Time
from config import ROOT_DIR
import os
import time as tm


class Simulation:
    def __init__(self, file_path: str, visualise: bool = True, dqn_agent=None):
        self.total_reward = None
        self.visualiser = None
        self.wait_time = None
        self.collision = None
        self.spawning = None
        self.model = None
        self.time = None
        self.uid = None
        self.reward = None
        self.dqn_agent = dqn_agent
        self.visualise = visualise
        self.file_path = file_path
        self.reset()

    def reset(self):
        self.time = 0.0
        self.uid = 0
        self.wait_time = [0]
        self.wait_time_vehicle_limit = 50
        self.model = Model()
        self.model.load_junction(self.file_path)
        self.collision = None
        self.reward = 0
        self.total_reward = 0

        self.model.set_start_time_of_day(Time(8, 0, 0))
        self.model.set_tick_rate(10)
        self.model.setup_random_spawning()
        self.model.generate_routes()

        if self.visualise:
            self.visualiser = JunctionVisualiser()
            self.visualiser.define_main(self.main)
            self.visualiser.load_junction(self.file_path)
            self.visualiser.set_scale(20)
            self.visualiser.open()

    def play(self):
        while self.total_reward
    def main(self):
        for i in range(100001):
            self.update(i)
        self.visualiser.close()

    def update(self, i: int, action: int = 0):
        penalty = self.take_action(action)

        time = self.model.calculate_time_of_day()
        for index, node_uid in enumerate(self.model.calculate_start_nodes()):
            spawn_info = self.model.nudge_spawner(node_uid, time)
            if spawn_info is not None:
                route_uid, length, width, distance_delta = spawn_info
                self.add_vehicle(route_uid, length, width)

        # if self.dqn_agent is not None:
        #     lights = self.model.get_lights()
        #     action = self.dqn_agent.forward(self.get_state())
        #     if action == 0:
        #         pass
        #     elif action == 1:
        #         lights[0].set_red()
        #     elif action == 2:
        #         lights[1].set_red()
        # else:

        for light in self.model.get_lights():
            light.update(self.model.tick_time)

        self.model.remove_finished_vehicles()
        coordinates_angle_size = []
        for vehicle in self.model.get_vehicles():
            vehicle_uid = vehicle.uid
            coordinates = self.model.get_coordinates(vehicle_uid)
            angle = self.model.get_angle(vehicle.uid)

            object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle_uid)
            vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead, self.model.get_curvature(vehicle_uid))
            vehicle.update_position_data(coordinates)
            if vehicle.get_speed() < 5:
                vehicle.add_wait_time(self.model.tick_time)

            route = self.model.get_route(vehicle.get_route_uid())
            path = self.model.get_path(route.get_path_uid(vehicle.get_path_index()))
            if vehicle.get_path_distance_travelled() >= path.get_length():
                if vehicle.get_path_index() + 1 == len(route.get_path_uids()):
                    self.wait_time.append(vehicle.get_wait_time())
                    self.wait_time = self.wait_time[-self.wait_time_vehicle_limit:]

            vehicle.update_position_data(list(coordinates))
            coordinates_angle_size.append([coordinates[0], coordinates[1], angle, vehicle.length, vehicle.width, vehicle.uid])

        self.collision = self.check_colision(coordinates_angle_size)


        self.reward = 30 - self.get_mean_wait_time() ** 2 + penalty + (i / 1000)
        if self.collision is not None:
            self.reward -= 5000

        self.total_reward += self.reward

        self.model.tock()
        # Update visualiser
        if self.visualise:
            self.visualiser.update_vehicle_positions(coordinates_angle_size)
            self.visualiser.update_light_colours(self.model.lights)
            self.visualiser.update_time(self.model.calculate_time_of_day())
            self.visualiser.update_collision_warning(True if self.collision is not None else False)
            sleep(self.model.tick_time)

        # if i % 200 == 0:
        #     self.model.get_lights()[random.choice([0, 1])].set_red()
        # print(f" {self.total_reward} / {i}")

    def take_action(self, action):
        penalty = 0
        if action == 0:
            pass
        elif action == 1:
            if self.model.get_lights()[0] == "green":
                self.set_red(0)
            else:
                penalty = -10000
        elif action == 2:
            if self.model.get_lights()[1] == "green":
                self.set_red(1)
            else:
                penalty = -10000
        return penalty

    def set_red(self, index):
        self.model.get_lights()[index].set_red()

    def get_state(self):
        return np.array(
            [
                self.get_path_occupancy(1),
                self.get_path_wait_time(1),
                self.get_mean_speed(1),
                self.get_path_occupancy(4),
                self.get_path_wait_time(4),
                self.get_mean_speed(4),
                self.model.get_lights()[0].get_state(),
                self.model.get_lights()[0].get_time_remaining(),
                self.model.get_lights()[1].get_state(),
                self.model.get_lights()[1].get_time_remaining(),
            ]
        )

    def get_path_occupancy(self, path_uid):
        state = 0
        for vehicle in self.model.get_vehicles():
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                state += 1
        return state

    def get_path_wait_time(self, path_uid):
        wait_time = 0
        for vehicle in self.model.get_vehicles():
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                wait_time += vehicle.get_wait_time()
        return wait_time

    def get_mean_speed(self, path_uid):
        speed = []
        for vehicle in self.model.get_vehicles():
            route = self.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                speed.append(vehicle.get_speed())
        return mean(speed)

    def get_mean_wait_time(self):
        return mean(self.wait_time)

    def get_lights(self):
        return self.model.get_lights()

    def add_vehicle(self, route_uid: int, length: float, width: float):
        self.uid += 1
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.time,
                route_uid=route_uid,
                speed=15.0,
                acceleration=0.0,
                maximum_acceleration=0.9,
                maximum_deceleration=4.0,
                preferred_time_gap=2.0,
                maximum_speed=30.0,
                length=length,
                width=width
            )
        )

    def check_colision(self, coordinates_angle_size: [[int, int, int, int, int, int]]):
        # TODO: Makes static and re-use
        lines = []
        for coordinate_angle_size in coordinates_angle_size:
            x, y, a, l, w, uid = coordinate_angle_size
            xy1, xy2, xy3, xy4 = calculate_rectangle_corner_coords(x, y, a, l, w)
            lines.append([xy1, xy2, uid])
            lines.append([xy2, xy3, uid])
            lines.append([xy3, xy4, uid])
            lines.append([xy4, xy1, uid])

        for i in range(len(lines)):
            x1_1, y1_1, x1_2, y1_2 = lines[i][0][0], lines[i][0][1], lines[i][1][0], lines[i][1][1]
            uid1 = lines[i][2]
            for j in range(i + 1, len(lines)):
                x2_1, y2_1, x2_2, y2_2 = lines[j][0][0], lines[j][0][1], lines[j][1][0], lines[j][1][1]
                uid2 = lines[j][2]
                if uid1 == uid2:
                    continue

                if x1_1 == x1_2 and x2_1 == x2_2:  # if line 1 and line 2 is vertical
                    if x1_1 == x2_1:  # If line 1 and lin 2 are both on the same x value
                        # Check if they overlap in the y direction
                        y1_min = min(y1_1, y1_2)
                        y1_max = max(y1_1, y1_2)
                        y2_min = min(y2_1, y2_2)
                        y2_max = max(y2_1, y2_2)
                        overlap_range = calculate_range_overlap(y1_min, y1_max, y2_min, y2_max)
                        if overlap_range is None:
                            continue
                        else:
                            return uid1, uid2
                    else:
                        continue

                elif x1_1 == x1_2:  # if line 1 is vertical
                    if min(x2_1, x2_2) <= x1_1 <= max(x2_1, x2_2):
                        m, c = calculate_line_gradient_and_constant(x2_1, y2_1, x2_2, y2_2)
                        y = m * x1_1 + c
                        if min(y1_1, y1_2) <= y <= max(y1_1, y1_2):
                            return uid1, uid2
                        else:
                            continue
                    else:
                        continue

                elif x2_1 == x2_2:  # if line 2 is vertical
                    if min(x1_1, x1_2) <= x2_1 <= max(x1_1, x1_2):
                        m, c = calculate_line_gradient_and_constant(x1_1, y1_1, x1_2, y1_2)
                        y = m * x2_1 + c
                        if min(y2_1, y2_2) <= y <= max(y2_1, y2_2):
                            return uid1, uid2
                        else:
                            continue
                    else:
                        continue

                else:
                    m1, c1 = calculate_line_gradient_and_constant(x1_1, y1_1, x1_2, y1_2)
                    m2, c2 = calculate_line_gradient_and_constant(x2_1, y2_1, x2_2, y2_2)

                    if m1 == m2 and c1 == c2:  # if they have the same gradient and intersection point
                        x1_min = min(x1_1, x1_2)
                        x1_max = max(x1_1, x1_2)
                        x2_min = min(x2_1, x2_2)
                        x2_max = max(x2_1, x2_2)
                        overlap_range = calculate_range_overlap(x1_min, x1_max, x2_min, x2_max)
                        if overlap_range is None:
                            continue
                        else:
                            return uid1, uid2

                    elif m1 == m2:  # if they have the same gradient (but different intersection point)
                        continue
                    else:
                        x1_min = min(x1_1, x1_2)
                        x1_max = max(x1_1, x1_2)
                        x2_min = min(x2_1, x2_2)
                        x2_max = max(x2_1, x2_2)
                        overlap_range = calculate_range_overlap(x1_min, x1_max, x2_min, x2_max)
                        if overlap_range is None:
                            continue
                        else:
                            x_cross = (c2 - c1) / (m1 - m2)
                            if overlap_range[0] <= x_cross <= overlap_range[1]:
                                return uid1, uid2
                            else:
                                continue
        return None


if __name__ == "__main__":
    sim = Simulation(os.path.join(ROOT_DIR, "Junction_Designs", "cross_road.junc"), visualise=True)
    for i in range(50001):
        sim.update(i)
