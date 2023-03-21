from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('../')

from gym.spaces import Discrete, Box
import numpy as np
from numpy import mean

"""

Spawn target car
inputs: vehicles infront / behind current vehicle change location
Run sim and change lane when ml model says so
Once lane changing occurs, run sim for X iterations
Calculate reward
reset

"""
from simulation.lane_changing.lc_simulation import Simulation


class SimulationManager:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_possible_actions = 2
        self.action_space = Discrete(self.number_of_possible_actions)

        # Inputs / States
        self.observation_space_size = 5  # distance from change point to car in front and car behind, speed of car in front and car behind, distance to end of lane
        self.observation_space = Box(0, 10, shape=(1, self.observation_space_size), dtype=float)

        # VEHICLE
        self.vehicle_uid = None
        self.lane_changed = False

        # REWARD
        self.default_reward = 0
        self.action_reward = -10000

        # Lane changing
        self.lane_changing_complete = 0
        self.lane_change_complete_reward = 100

        # Crashes
        self.crash_reward = -10000

        # Distance along path lane change
        self.distance_to_end_of_path_reward = 50
        self.distance_to_car_in_front_reward = 50
        self.distance_to_car_behind_reward = 50
        self.distance_to_car_in_front_reward_limit = 2000
        self.distance_to_car_behind_reward_limit = 2000


        # Change in other vehicle speeds
        self.acceleration_other_vehicles_reward = 10

        self.pre_train_sim_iterations = 1000  # 100 seconds
        self.post_spawn_sim_iterations = 10  # 3 seconds

        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        for iteration in range(self.pre_train_sim_iterations):
            simulation.compute_single_iteration()
        last_car = simulation.get_last_vehicle_uid_spawned()
        while simulation.get_last_vehicle_uid_spawned() == last_car:
            simulation.compute_single_iteration(lane_change=True)
        self.vehicle_uid = simulation.get_last_vehicle_uid_spawned()
        simulation.highlight_vehicles.append(self.vehicle_uid)
        for iteration in range(self.post_spawn_sim_iterations):
            simulation.compute_single_iteration()
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()

        self.lane_changed = False

        return np.zeros(self.observation_space_size)

    def take_action(self, action_index):
        if action_index == 0:
            pass
        elif action_index == 1:
            self.simulation.change_lane(self.vehicle_uid)

    def compute_simulation_metrics(self):
        self.check_lane_change_flag()

    def check_lane_change_flag(self):
        vehicle = self.simulation.model.get_vehicle(self.vehicle_uid)
        if vehicle.changing_lane:
            self.lane_changed = True

    def calculate_reward(self, step):
        reward = self.default_reward
        reward += self.calculate_crash_reward()
        # if self.acceleration_other_vehicles_reward != 0:
        #     reward += self.acceleration_other_vehicles_reward * self.get_acceleration_other_vehicles_behind()
        reward += self.calcualte_distance_to_end_of_path_reward()

        return reward

    def calculate_crash_reward(self):
        if self.crash_reward != 0:
            return self.crash_reward * self.get_crash()

    def calcualte_distance_to_end_of_path_reward(self):
        if self.distance_to_end_of_path_reward != 0:
            return self.distance_to_end_of_path_reward * self.get_distance_to_end_of_path(self.vehicle_uid)

    def calculate_distance_to_car_in_front_reward(self):
        if self.distance_to_car_in_front_reward != 0:
            vehicle_distance_travelled = self.simulation.model.get_vehicle(self.vehicle_uid).get_path_distance_travelled()
            path_uid = self.simulation.model.get_vehicle_path_uid(self.vehicle_uid)
            distance_to_vehicle_in_front, ignore = self.get_distance_to_vehicle_in_front(vehicle_distance_travelled, path_uid)
            return min(self.distance_to_car_in_front_reward * distance_to_vehicle_in_front, self.distance_to_car_in_front_reward_limit)

    def calculate_distance_to_car_behind_reward(self):
        if self.distance_to_car_in_front_reward != 0:
            vehicle_distance_travelled = self.simulation.model.get_vehicle(self.vehicle_uid).get_path_distance_travelled()
            path_uid = self.simulation.model.get_vehicle_path_uid(self.vehicle_uid)
            distance_to_vehicle_behind, ignore = self.get_distance_to_vehicle_behind(vehicle_distance_travelled, path_uid)
            return min(self.distance_to_car_behind_reward * distance_to_vehicle_behind, self.distance_to_car_behind_reward_limit)

    def get_state(self):

        if self.lane_changed or self.check_vehicle_reached_end_of_path():
            return None

        distance_to_vehicle_behind, vehicle_behind = self.get_distance_to_vehicle_behind_change_location(self.vehicle_uid)
        distance_to_vehicle_in_front, vehicle_in_front = self.get_distance_to_vehicle_in_front_of_change_location(self.vehicle_uid)

        if vehicle_behind is None:
            min_path_distance_travelled = float('inf')
            vehicle_behind_speed = float('inf')
        else:
            vehicle_behind_speed = vehicle_behind.get_speed()

        if vehicle_in_front is None:
            max_path_distance_travelled = float('inf')
            vehicle_in_front_speed = float('inf')
        else:
            vehicle_in_front_speed = vehicle_in_front.get_speed()

        return np.array(
            [
                self.get_distance_to_end_of_path(self.vehicle_uid),
                distance_to_vehicle_behind,
                distance_to_vehicle_in_front,
                vehicle_behind_speed,
                vehicle_in_front_speed
            ]
        )

    def get_distance_to_end_of_path(self, vehicle_uid):
        path_uid = self.simulation.model.get_vehicle_path_uid(self.vehicle_uid)
        path_length = self.simulation.model.get_path(path_uid).get_length()
        vehicle = self.simulation.model.get_vehicle(self.vehicle_uid)
        distance_traveled = vehicle.get_path_distance_travelled()
        return path_length - distance_traveled

    def get_distance_to_vehicle_in_front_of_change_location(self, vehicle_uid):
        path_distance_after_lane_change = self.simulation.model.get_vehicle_path_length_after_lane_change(vehicle_uid)
        path_uid_after_lane_change = self.simulation.model.get_vehicle_next_path_uid(vehicle_uid)

        return self.get_distance_to_vehicle_in_front(path_distance_after_lane_change, path_uid_after_lane_change)

    def get_distance_to_vehicle_in_front(self, vehicle_path_distance, vehicle_path):
        # Search the current path
        min_path_distance_travelled = float('inf')
        vehicle_in_front = None
        for that_vehicle in self.simulation.model.vehicles:
            that_path_uid = self.simulation.model.get_route(that_vehicle.get_route_uid()).get_path_uid(that_vehicle.get_path_index())
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()
            if that_path_uid == vehicle_path and min_path_distance_travelled > that_vehicle_path_distance_travelled > vehicle_path_distance:
                min_path_distance_travelled = that_vehicle_path_distance_travelled
                vehicle_in_front = that_vehicle

        distance_in_front = min_path_distance_travelled - vehicle_path_distance
        assert distance_in_front > 0
        return distance_in_front, vehicle_in_front

    def get_distance_to_vehicle_behind_change_location(self, vehicle_uid):
        path_distance_after_lane_change = self.simulation.model.get_vehicle_path_length_after_lane_change(vehicle_uid)
        path_uid_after_lane_change = self.simulation.model.get_vehicle_next_path_uid(vehicle_uid)

        return self.get_distance_to_vehicle_behind(path_distance_after_lane_change, path_uid_after_lane_change)

    def get_distance_to_vehicle_behind(self, vehicle_path_distance, vehicle_path):
        # Search the current path
        max_path_distance_travelled = 0
        vehicle_behind = None
        for that_vehicle in self.simulation.model.vehicles:
            that_path_uid = self.simulation.model.get_route(that_vehicle.get_route_uid()).get_path_uid(
                that_vehicle.get_path_index())
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()
            if that_path_uid == vehicle_path and vehicle_path_distance > that_vehicle_path_distance_travelled > max_path_distance_travelled:
                max_path_distance_travelled = that_vehicle_path_distance_travelled
                vehicle_behind = that_vehicle

        distance_behind = vehicle_path_distance - max_path_distance_travelled
        assert distance_behind > 0

        return distance_behind, vehicle_behind


    # REWARD FUNCTIONS

    def get_crash(self):
        return 1 if self.simulation.model.detect_collisions() else 0

    def get_acceleration_other_vehicles_behind(self):
        sum_acceleration = 0
        vehicle_path = self.simulation.model.get_vehicle_path_uid(
            self.vehicle_uid)
        that_vehicle_path_distance_travelled = self.simulation.model.get_vehicle(
            self.vehicle_uid).get_path_distance_travelled()
        for vehicle in self.simulation.model.vehicles:
            that_path = self.simulation.model.get_path(self.simulation.model.get_route(
                vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
            that_vehicle_path_distance_travelled = vehicle.get_path_distance_travelled()
            if (vehicle.uid != self.vehicle_uid) and that_path == vehicle_path and that_vehicle_path_distance_travelled < vehicle_distance_travelled:
                sum_acceleration += vehicle.get_acceleration()
        return sum_acceleration

    def get_lane_change_complete(self):
        return self.lane_changing_complete

    def check_vehicle_reached_end_of_path(self):
        vehicle = self.simulation.model.get_vehicle(self.vehicle_uid)
        if not self.lane_changed and vehicle.get_path_index() != 0:
            return True
        else:
            return False
