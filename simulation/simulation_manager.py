from platform import system

from library.infrastructure import TrafficLight
from library.vehicles import Vehicle

if system() == 'Windows':
    import sys
    sys.path.append('./')

from gym import Env
from gym.spaces import Discrete, Box, Dict
import numpy as np
from numpy import mean

from simulation.simulation import Simulation


class SimulationManager:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_possible_actions, self.action_space = self.calculate_actions()

        # Inputs / States
        self.observation_space_size = 10
        self.observation_space = Box(0, 10, shape=(1, self.observation_space_size), dtype=float)

        # REWARD
        self.default_reward = 30
        self.action_reward = -10000
        # Duration
        self.simulation_duration_reward = 0.001
        # Crash
        self.crash_reward = -5000
        # Waiting
        self.waiting_speed = 5
        self.num_cars_waiting_reward = 0
        self.wait_time = None
        self.wait_time_vehicle_limit = None
        # Total waiting
        self.total_wait_time_reward = 0
        self.total_wait_time_exp_reward = 0
        self.total_wait_time_exponent = 0
        # Mean Waiting
        self.mean_wait_time_reward = 0
        self.mean_wait_time_exp_reward = -1
        self.mean_wait_time_exponent = 2

        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def calculate_actions(self):
        number_of_actions = len(self.simulation.model.lights) + 1
        return number_of_actions, Discrete(number_of_actions)

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
            if self.simulation.model.lights[action_index - 1].colour == "green":
                self.simulation.model.lights[action_index - 1].set_red()
            else:
                penalty = self.action_reward
        return penalty

    def compute_simulation_metrics(self):
        self.update_vehicle_wait_time()
        self.compute_all_wait_times()

    def update_vehicle_wait_time(self):
        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < self.waiting_speed:
                vehicle.add_wait_time(self.simulation.model.tick_time)

    def compute_all_wait_times(self):
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            path = self.simulation.model.get_path(route.get_path_uid(vehicle.get_path_index()))
            if vehicle.get_path_distance_travelled() >= path.get_length():
                if vehicle.get_path_index() + 1 == len(route.get_path_uids()):
                    self.wait_time.append(vehicle.get_wait_time())
                    self.wait_time = self.wait_time[-self.wait_time_vehicle_limit:]

    def calculate_reward(self, action_reward, step):
        reward = self.default_reward
        reward += action_reward
        if self.simulation_duration_reward != 0:
            reward += self.simulation_duration_reward * step
        if self.crash_reward != 0:
            reward += self.crash_reward * self.get_crash()
        if self.num_cars_waiting_reward != 0:
            reward += self.num_cars_waiting_reward * self.get_number_of_vehicles_waiting()
        if self.total_wait_time_reward != 0:
            reward += self.total_wait_time_reward * self.get_total_vehicle_wait_time()
        if self.total_wait_time_exp_reward != 0:
            reward += self.total_wait_time_exp_reward * self.get_total_vehicle_wait_time_exp(self.total_wait_time_exponent)
        if self.mean_wait_time_reward != 0:
            reward += self.mean_wait_time_reward * self.get_mean_wait_time()
        if self.mean_wait_time_exp_reward != 0:
            reward += self.mean_wait_time_exp_reward * self.get_mean_wait_time_exp(self.mean_wait_time_exponent)

        return reward

    def get_state(self):
        return np.array(
            [
                self.get_path_occupancy(1),
                self.get_path_wait_time(1),
                self.get_mean_speed(1),
                self.get_path_occupancy(4),
                self.get_path_wait_time(4),
                self.get_mean_speed(4),
                self.simulation.model.lights[0].get_state(),
                self.simulation.model.lights[0].get_time_remaining(),
                self.simulation.model.lights[1].get_state(),
                self.simulation.model.lights[1].get_time_remaining(),
            ]
        )

    def get_path_occupancy(self, path_uid):
        state = 0
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                state += 1
        return state

    def get_path_wait_time(self, path_uid):
        wait_time = 0
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                wait_time += vehicle.waiting_time
        return wait_time

    def get_mean_speed(self, path_uid):
        speed = []
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            if path_uid == route.get_path_uid(vehicle.get_path_index()):
                speed.append(vehicle.get_speed())
        return mean(speed)

    def get_lights(self):
        return self.simulation.model.get_lights()

    # REWARD FUNCTIONS

    def get_crash(self):
        return 1 if len(self.simulation.model.detect_collisions()) > 0 else 0

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