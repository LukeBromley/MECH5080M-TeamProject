import random
from platform import system

from library.infrastructure import TrafficLight
from library.vehicles import Vehicle

if system() == 'Windows':
    import sys
    sys.path.append('../')

from gym.spaces import Discrete, Box
import numpy as np
from numpy import mean

from simulation.junction.simulation import Simulation


class SimulationManager:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_possible_actions, self.action_space = self.calculate_actions()

        # Metrics
        self.wait_time = None
        self.wait_time_vehicle_limit = None
        # TODO: Soft code the id's
        self.light_controlled_path_uids = [1, 4]

        # Inputs / States
        self.features_per_state_input = 2
        self.number_of_tracked_vehicles_per_path = 6
        self.observation_space_size = self.features_per_state_input * len(self.light_controlled_path_uids) * (1 + self.number_of_tracked_vehicles_per_path)
        # TODO: Initialize separate boxes by argmax for different inputs
        self.observation_space = Box(0, 30, shape=(1, self.observation_space_size), dtype=float)

        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def calculate_actions(self):
        number_of_actions = 2 * len(self.simulation.model.lights) + 1
        return number_of_actions, list(range(number_of_actions))

    def reset(self):
        self.simulation = self.create_simulation()

        # # State
        self.wait_time = [0]
        self.wait_time_vehicle_limit = 20

        return np.zeros(self.observation_space_size)

    def take_action(self, action_index):
        penalty = 0
        if action_index == 0:
            pass
        elif action_index == 1:
            light = self.simulation.model.lights[0]
            if light.colour == "green":
                light.set_red()
            else:
                penalty = 1000
        elif action_index == 2:
            light = self.simulation.model.lights[1]
            if light.colour == "green":
                light.set_red()
            else:
                penalty = 1000
        elif action_index == 3:
            light = self.simulation.model.lights[0]
            if light.colour == "red":
                light.set_green()
            else:
                penalty = 1000
        elif action_index == 4:
            light = self.simulation.model.lights[1]
            if light.colour == "red":
                light.set_green()
            else:
                penalty = 1000
        return penalty

    def get_vehicle_state(self, vehicle: Vehicle):
        return [
            vehicle.get_path_distance_travelled(),
            vehicle.get_speed()
            # vehicle.wait_time
            # vehicle.get_length(),
            # vehicle.get_acceleration()
        ]

    def get_traffic_light_state(self, light: TrafficLight):
        return [
            light.get_state(),
            light.get_time_remaining()
        ]

    def get_state(self):
        inputs = []
        for light in self.simulation.model.lights:
            inputs += self.get_traffic_light_state(light)

        path_inputs = [[] for _ in self.light_controlled_path_uids]
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            path_uid = route.get_path_uid(vehicle.get_path_index())
            if path_uid in self.light_controlled_path_uids:
                path_inputs[self.light_controlled_path_uids.index(path_uid)] += self.get_vehicle_state(vehicle)

        for path_input in path_inputs:
            inputs += self.pad_state_input(path_input)

        return inputs

    def pad_state_input(self, state_input: list):
        # TODO: Soft code the traffic light state size
        state_input = state_input[0: self.features_per_state_input * self.number_of_tracked_vehicles_per_path]
        state_input += [np.NAN] * (self.features_per_state_input * self.number_of_tracked_vehicles_per_path - int(len(state_input)))

        # # TODO: Implement shuffling
        # tupled_state_input = []
        # for index in range(0, len(state_input), 2):
        #     tupled_state_input.append((state_input[index], state_input[index + 1]))
        # random.shuffle(tupled_state_input)
        #
        # state_input = []
        # for tuple in tupled_state_input:
        #     state_input += tuple
        return state_input

    def compute_simulation_metrics(self):
        for vehicle in self.simulation.model.removed_vehicles:
            self.wait_time.append(vehicle.wait_time)

        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < 5:
                vehicle.add_wait_time(self.simulation.model.tick_time)

    def calculate_reward(self):
        reward = 100 - self.get_mean_wait_time() ** 2
        if self.simulation.model.detect_collisions():
            reward -= 50000
        return reward

    def get_mean_wait_time(self):
        return mean(self.wait_time[-self.wait_time_vehicle_limit:])

    def get_sum_wait_time(self):
        return sum(self.wait_time)

    def get_lights(self):
        return self.simulation.model.get_lights()

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