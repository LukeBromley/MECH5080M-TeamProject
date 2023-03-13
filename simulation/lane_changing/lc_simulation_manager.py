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
        self.default_reward = 30
        self.action_reward = -10000
        # Duration
        self.simulation_duration_reward = 0.001
        #

        self.pre_train_sim_iterations = 1000 #100 seconds

        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        for iteration in range(self.pre_train_sim_iterations):
            simulation.compute_single_iteration()
        last_car = simulation.get_last_vehicle_uid_spawned()
        while simulation.get_last_vehicle_uid_spawned() == last_car:
            simulation.compute_single_iteration()
        self.vehicle_uid = simulation.get_last_vehicle_uid_spawned()
        simulation.highlight_vehicles.append(self.vehicle_uid)
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()

        self.lane_changed = False

        return np.asarray(np.zeros(self.observation_space_size)).astype('float32')

    def take_action(self, action_index):
        if action_index == 0:
            pass
        else:
            self.simulation.change_lane(self.vehicle_uid)

    def compute_simulation_metrics(self):
        self.check_lane_change_flag()

    def check_lane_change_flag(self):
        vehicle = self.simulation.model.get_vehicle(self.vehicle_uid)
        if vehicle.changing_lane:
            self.lane_changed = True

    def calculate_reward(self, step):
        reward = self.default_reward
        # reward += action_reward
        # if self.simulation_duration_reward != 0:
        #     reward += self.simulation_duration_reward * step
        # if self.crash_reward != 0:
        #     reward += self.crash_reward * self.get_crash()
        # if self.num_cars_waiting_reward != 0:
        #     reward += self.num_cars_waiting_reward * self.get_number_of_vehicles_waiting()
        # if self.total_wait_time_reward != 0:
        #     reward += self.total_wait_time_reward * self.get_total_vehicle_wait_time()
        # if self.total_wait_time_exp_reward != 0:
        #     reward += self.total_wait_time_exp_reward * self.get_total_vehicle_wait_time_exp(self.total_wait_time_exponent)
        # if self.mean_wait_time_reward != 0:
        #     reward += self.mean_wait_time_reward * self.get_mean_wait_time()
        # if self.mean_wait_time_exp_reward != 0:
        #     reward += self.mean_wait_time_exp_reward * self.get_mean_wait_time_exp(self.mean_wait_time_exponent)

        return reward

    def get_state(self):
        distance_to_end_of_path = self.get_distance_to_end_of_path(self.vehicle_uid)
        distance_to_vehicle_in_front, vehicle_in_front = self.get_distance_to_vehicle_in_front_of_change_location(self.vehicle_uid)
        distance_to_vehicle_behind, vehicle_behind = self.get_distance_to_vehicle_behind_change_location(self.vehicle_uid)

        return np.array(
            [
                distance_to_end_of_path,
                distance_to_vehicle_in_front,
                distance_to_vehicle_behind,
                vehicle_in_front.get_speed(),
                vehicle_behind.get_speed()
            ]
        )

    def get_distance_to_end_of_path(self, vehicle_uid):
        path_uid = self.simulation.model.get_vehicle_path_uid(vehicle_uid)
        path_length = self.simulation.model.get_path(path_uid).get_length()
        vehicle = self.simulation.model.get_vehicle(vehicle_uid)
        distance_traveled = vehicle.get_path_distance_travelled()
        return path_length - distance_traveled

    def get_distance_to_vehicle_in_front_of_change_location(self, vehicle_uid):
        path_distance_after_lane_change = self.simulation.model.get_vehicle_path_length_after_lane_change(vehicle_uid)
        path_uid_after_lane_change = self.simulation.model.get_vehicle_next_path_uid(vehicle_uid)

        # Search the current path
        min_path_distance_travelled = float('inf')
        for that_vehicle in self.simulation.model.vehicles:
            that_path_uid = self.simulation.model.get_route(that_vehicle.get_route_uid()).get_path_uid(that_vehicle.get_path_index())
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()
            if that_path_uid == path_uid_after_lane_change and min_path_distance_travelled > that_vehicle_path_distance_travelled > path_distance_after_lane_change:
                min_path_distance_travelled = that_vehicle_path_distance_travelled

        return min_path_distance_travelled, that_vehicle

    def get_distance_to_vehicle_behind_change_location(self, vehicle_uid):
        path_distance_after_lane_change = self.simulation.model.get_vehicle_path_length_after_lane_change(vehicle_uid)
        path_uid_after_lane_change = self.simulation.model.get_vehicle_next_path_uid(vehicle_uid)

        # Search the current path
        max_path_distance_travelled = 0
        for that_vehicle in self.simulation.model.vehicles:
            that_path_uid = self.simulation.model.get_route(that_vehicle.get_route_uid()).get_path_uid(
                that_vehicle.get_path_index())
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()
            if that_path_uid == path_uid_after_lane_change and path_distance_after_lane_change > that_vehicle_path_distance_travelled > max_path_distance_travelled:
                max_path_distance_travelled = that_vehicle_path_distance_travelled

        return max_path_distance_travelled, that_vehicle

    # REWARD FUNCTIONS

    def get_crash(self):
        return 1 if self.simulation.model.detect_collisions() else 0

    def get_number_of_vehicles_waiting(self):
        number_of_cars_waiting = 0
        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < self.waiting_speed:
                number_of_cars_waiting += 1
        return number_of_cars_waiting

    def get_total_vehicle_wait_time(self):
        return sum(self.wait_time)

    def get_total_vehicle_wait_time_exp(self, exponent):
        return self.get_total_vehicle_wait_time()**exponent

    def get_mean_wait_time(self):
        return mean(self.wait_time)

    def get_mean_wait_time_exp(self, exponent):
        return self.get_mean_wait_time()**exponent

    def get_summed_speed_of_all_vehicles(self):
        sum_car_speed = 0
        for vehicle in self.simulation.model.vehicles:
            sum_car_speed += vehicle.get_speed()
        return sum_car_speed