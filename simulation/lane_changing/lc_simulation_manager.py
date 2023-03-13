from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('../')

from gym.spaces import Discrete, Box
import numpy as np
from numpy import mean

"""

Create random environemnt of cars positioned along lanes
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
        self.simulation = Simulation(
            self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_possible_actions = 2
        self.action_space = Discrete(self.number_of_possible_actions)

        # Inputs / States
        # distance from change point to car in front and car behind, speed of car in front and car behind, distance to end of lane
        self.observation_space_size = 5
        self.observation_space = Box(0, 10, shape=(
            1, self.observation_space_size), dtype=float)

        # VEHICLE
        self.vehicle_uid = None

        # REWARD
        self.default_reward = 30

        # Lane changing
        self.lane_changing_complete = 0
        self.lane_change_complete_reward = 100

        # Crashes
        self.crash_reward = -1000

        # Distance along path lane change
        self.distance_to_end_of_path_reward = 50

        # Change in other vehicle speeds
        self.slowing_other_vehicles_reward = -10

        self.pre_train_sim_iterations = 1000  # 100 seconds

        self.reset()

    def create_simulation(self):
        simulation = Simulation(
            self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        for iteration in range(self.pre_train_sim_iterations):
            simulation.compute_single_iteration()
        last_car = simulation.get_last_vehicle_uid_spawned()
        while (simulation.get_last_vehicle_uid_spawned() == last_car):
            simulation.compute_single_iteration()
        self.vehicle_uid = simulation.get_last_vehicle_uid_spawned()
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()

        # # State
        self.wait_time = [0]
        self.wait_time_vehicle_limit = 50

        return np.asarray(np.zeros(self.observation_space_size)).astype('float32')

    def take_action(self, action_index):
        penalty = 0
        if action_index == 0:
            pass
        else:
            self.simulation.change_lane(self.vehicle_uid)
            self.lane_changing_complete = 1
        return penalty

    def calculate_reward(self, action_reward, step):
        reward = self.default_reward
        if self.crash_reward != 0:
            reward += self.crash_reward * self.get_crash()
        if self.lane_change_complete_reward != 0:
            reward += self.lane_change_complete_reward * self.get_lane_change_complete()
        if self.distance_to_end_of_path_reward != 0:
            reward += self.distance_to_end_of_path_reward * self.get_distance_to_end_of_path()
        if self.slowing_other_vehicles_reward != 0:
            reward += self.slowing_other_vehicles_reward * \
                self.get_slowing_other_vehicles_behind()

        return reward

    def get_state(self):
        return np.array(
            [
                self.get_distance_to_end_of_path(self.vehicle_uid)
            ]
        )

    def get_distance_to_end_of_path(self, vehicle_uid):
        path_uid = self.simulation.model.get_vehicle_path_uid(vehicle_uid)
        path_length = self.simulation.model.get_path(path_uid).get_length()
        vehicle = self.simulation.model.get_vehicle(vehicle_uid)
        distance_traveled = vehicle.get_path_distance_travelled()
        return path_length - distance_traveled

    def get_distance_to_vehicle_in_front_of_change_location(self, vehicle_uid):
        this_vehicle_path_distance_travelled = self.simulation.model.get_vehicle_path_length_after_lane_change(
            vehicle_uid)

        # Search the current path
        min_path_distance_travelled = float('inf')
        for that_vehicle in self.simulation.model.vehicles:
            that_path = self.simulation.model.get_path(self.simulation.model.get_route(
                that_vehicle.get_route_uid()).get_path_uid(that_vehicle.get_path_index()))
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()

            if that_path.uid == this_path.uid and min_path_distance_travelled > that_vehicle_path_distance_travelled > this_vehicle_path_distance_travelled:
                min_path_distance_travelled = that_vehicle_path_distance_travelled
                object_ahead = that_vehicle

    # REWARD FUNCTIONS

    def get_crash(self):
        return 1 if len(self.simulation.model.detect_collisions()) > 0 else 0

    def get_summed_speed_of_all_vehicles(self):
        sum_car_speed = 0
        for vehicle in self.simulation.model.vehicles:
            sum_car_speed += vehicle.get_speed()
        return sum_car_speed

    def get_slowing_other_vehicles_behind(self):
        pass

    def get_lane_change_complete(self):
        return self.lane_changing_complete
