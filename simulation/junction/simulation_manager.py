import itertools
import random
from platform import system

from library.infrastructure import TrafficLight
from library.vehicles import Vehicle
from itertools import chain

if system() == 'Windows':
    import sys
    sys.path.append('../')

from gym.spaces import Discrete, Box
import numpy as np
from numpy import mean

from simulation.junction.simulation import Simulation


class SimulationManager:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.action_table = None
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_possible_actions, self.action_space = self.calculate_actions()

        # Metrics
        self.wait_time = []

        # TODO: Soft code the id's
        self.light_controlled_path_uids = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14]

        # Inputs / States
        self.features_per_state_input = 4
        self.number_of_tracked_vehicles_per_path = 5
        self.observation_space_size = self.features_per_state_input * len(self.light_controlled_path_uids) * (0 + self.number_of_tracked_vehicles_per_path)
        # TODO: Initialize separate boxes by argmax for different inputs
        self.observation_space = Box(0, 50, shape=(1, self.observation_space_size), dtype=float)
        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def calculate_actions(self):
        self.action_table = []
        number_of_lights = len(self.simulation.model.lights)
        for index in range(number_of_lights + 1):
            self.action_table += list(itertools.combinations(list(range(number_of_lights)), index))
        number_of_actions = 2**len(self.simulation.model.lights)
        return number_of_actions, Discrete(number_of_actions)

    def reset(self):
        self.simulation = self.create_simulation()
        self.wait_time = []

        return np.zeros(self.observation_space_size)

    def take_action(self, action_index):
        penalty = 0
        lights_to_turn_green = self.action_table[action_index]
        for index, light in enumerate(self.simulation.model.lights):
            if index in lights_to_turn_green:
                light.set_green()
            else:
                light.set_red()

        return penalty
        # if action_index == 0:
        #     self.simulation.model.lights[0].set_green()
        #     self.simulation.model.lights[1].set_green()
        # elif action_index == 1:
        #     self.simulation.model.lights[0].set_red()
        #     self.simulation.model.lights[1].set_green()
        #     # if light.colour == "green":
        #     #     light.set_red()
        #     # else:
        #     #     penalty = 1000
        # elif action_index == 2:
        #     self.simulation.model.lights[1].set_red()
        #     self.simulation.model.lights[0].set_green()
        #     # if light.colour == "green":
        #     #     light.set_red()
        #     # else:
        #     #     penalty = 1000
        # elif action_index == 3:
        #     self.simulation.model.lights[0].set_red()
        #     self.simulation.model.lights[1].set_red()
        #     # if light.colour == "red":
        #     #     light.set_green()
        #     # else:
        #     #     penalty = 1000
        # else:
        #     raise Exception("invalid action")
        # elif action_index == 4:
        #     self.simulation.model.lights[1].set_green()
        #     # if light.colour == "red":
        #     #     light.set_green()
        #     # else:
        #     #     penalty = 1000
        return penalty

    def get_vehicle_state(self, vehicle: Vehicle):
        return [
            vehicle.get_path_distance_travelled(),
            vehicle.get_speed(),
            vehicle.wait_time
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
        # for light in self.simulation.model.lights:
        #     inputs += self.get_traffic_light_state(light)

        path_inputs = [[] for _ in self.light_controlled_path_uids]
        for vehicle in self.simulation.model.vehicles:
            route = self.simulation.model.get_route(vehicle.get_route_uid())
            path_uid = route.get_path_uid(vehicle.get_path_index())
            if path_uid in self.light_controlled_path_uids:
                path_inputs[self.light_controlled_path_uids.index(path_uid)].append(self.get_vehicle_state(vehicle) + [path_uid])

        # Sort and flatten the inputs by distance travelled
        for index, path_input in enumerate(path_inputs):
            sorted_path_input = sorted(path_input, key=lambda features: features[0], reverse=True)
            flattened_path_input = list(chain.from_iterable(sorted_path_input))
            path_inputs[index] = flattened_path_input

        for path_input in path_inputs:
            inputs += self.pad_state_input(path_input)

        return inputs

    def pad_state_input(self, state_input: list):
        if len(state_input) > self.features_per_state_input * self.number_of_tracked_vehicles_per_path:
            state_input = state_input[:self.features_per_state_input * self.number_of_tracked_vehicles_per_path]
        else:
            state_input += [0.0] * (self.features_per_state_input * self.number_of_tracked_vehicles_per_path - len(state_input))

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
        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < 1:
                vehicle.add_wait_time(self.simulation.model.tick_time)
            elif vehicle.get_speed() > 2:
                vehicle.wait_time = 0.0
        # TODO: Implement weighted average
        self.wait_time = [vehicle.wait_time for vehicle in self.simulation.model.vehicles]

    def get_mean_wait_time(self):
        if self.wait_time:
            wait_time = self.wait_time
            wait_time.sort()

            dot_product = 0
            sum_coeff = 0

            for index, value in enumerate(wait_time):
                sum_coeff += (index + 1)**2
                dot_product += value * (index+1)**2
            return dot_product / sum_coeff
        else:
            return 0.0

    def calculate_reward(self):
        reward = 100 - self.get_mean_wait_time()**2
        if self.simulation.model.detect_collisions():
            reward -= 10000
        return reward / 1000

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

    def get_summed_speed_of_all_vehicles(self):
        sum_car_speed = 0
        for vehicle in self.simulation.model.vehicles:
            sum_car_speed += vehicle.get_speed()
        return sum_car_speed