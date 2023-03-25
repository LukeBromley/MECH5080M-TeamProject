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

        # TODO: Soft code the id's
        self.light_controlled_path_uids = [1, 4]
        self.light_path_uids = [2, 5]

        # Inputs / States
        self.features_per_state_input = 4
        self.number_of_tracked_vehicles_per_path = 4
        self.observation_space_size = self.features_per_state_input * len(self.light_controlled_path_uids) * (self.number_of_tracked_vehicles_per_path)

        self.light_controlled_path_uids += self.light_path_uids
        self.observation_space_size += self.features_per_state_input * 2 * len(self.light_path_uids)

        # TODO: Initialize separate boxes by argmax for different inputs
        self.observation_space = Box(0, 50, shape=(1, self.observation_space_size), dtype=float)
        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()
        self.freeze_traffic()
        return np.zeros(self.observation_space_size)

    def freeze_traffic(self, n: int = None):
        if n is None:
            n = random.randint(15 * self.simulation.model.tick_rate, 20 * self.simulation.model.tick_rate)

        for light in self.simulation.model.lights:
            light.set_state("red")

        for step in range(n):
            self.simulation.compute_single_iteration()

    def calculate_actions(self):
        self.action_table = []
        number_of_lights = len(self.simulation.model.lights)
        for index in range(number_of_lights + 1):
            self.action_table += list(itertools.combinations(list(range(number_of_lights)), index))
        number_of_actions = 2**len(self.simulation.model.lights)
        print(self.action_table)
        return number_of_actions, Discrete(number_of_actions)

    def get_illegal_actions(self):
        lights = self.simulation.model.lights
        illegal_actions = []
        for action_index, action in enumerate(self.action_table):
            legal = True
            for light_index, light in enumerate(lights):
                if light_index in action:
                    if light.colour == "green" or light.allows_change():
                        continue
                    else:
                        legal = False
                        break
                else:
                    if light.colour == "red" or light.allows_change():
                        continue
                    else:
                        legal = False
                        break
            if not legal:
                illegal_actions.append(action_index)
        return illegal_actions

    def get_legal_actions(self):
        lights = self.simulation.model.lights
        legal_actions = []
        for action_index, action in enumerate(self.action_table):
            legal = True
            for light_index, light in enumerate(lights):
                if light_index in action:
                    if light.colour == "green" or light.allows_change():
                        continue
                    else:
                        legal = False
                        break
                else:
                    if light.colour == "red" or light.allows_change():
                        continue
                    else:
                        legal = False
                        break
            if legal:
                legal_actions.append(action_index)
        return legal_actions

    def take_action(self, action_index):
        if action_index is not None:
            green_lights = self.action_table[action_index]
            for index, light in enumerate(self.simulation.model.lights):
                if index in green_lights:
                    light.set_state("green")
                else:
                    light.set_state("red")

    def get_vehicle_state(self, vehicle: Vehicle):
        return [
            vehicle.get_path_distance_travelled(),
            vehicle.get_speed(),
            vehicle.wait_time
            # vehicle.get_length(),
            # vehicle.get_acceleration()
        ]

    def get_state(self):
        # TODO: Add info about vehicles past the traffic light
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
            # Sorted adds more weight to the neural inputs of vehicles close to the traffic light
            sorted_path_input = sorted(path_input, key=lambda features: features[0], reverse=True)
            flattened_path_input = list(chain.from_iterable(sorted_path_input))
            path_inputs[index] = flattened_path_input

        for index, path_input in enumerate(path_inputs):
            if index < 2:
                inputs += self.pad_state_input(path_input, self.number_of_tracked_vehicles_per_path)
            else:
                inputs += self.pad_state_input(path_input, 2)
        return inputs

    def pad_state_input(self, state_input: list, n: int):
        if len(state_input) > self.features_per_state_input * n:
            state_input = state_input[:self.features_per_state_input * n]
        else:
            state_input += [np.NAN] * (self.features_per_state_input * n - len(state_input))

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

    def get_mean_wait_time(self):
        wait_times = [vehicle.wait_time for vehicle in self.simulation.model.vehicles]
        if wait_times:
            wait_times.sort()

            dot_product = 0
            sum_coeff = 0

            for index, value in enumerate(wait_times):
                sum_coeff += (index + 1)**2
                dot_product += value * (index+1)**2
            return dot_product / sum_coeff
        else:
            return 0.0

    def get_sum_wait_time(self):
        return sum([vehicle.wait_time for vehicle in self.simulation.model.vehicles])

    def get_lights(self):
        return self.simulation.model.get_lights()

    # REWARD FUNCTIONS

    def get_crash(self):
        return 1 if self.simulation.model.detect_collisions() else 0

    def get_number_of_vehicles_waiting(self):
        number_of_cars_waiting = 0
        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < 3:
                number_of_cars_waiting += 1
        return number_of_cars_waiting

    def get_total_vehicle_wait_time(self):
        return sum([vehicle.wait_time for vehicle in self.simulation.model.vehicles])

    def get_total_vehicle_wait_time_exp(self, exponent):
        return self.get_total_vehicle_wait_time()**exponent

    def get_summed_speed_of_all_vehicles(self):
        sum_car_speed = 0
        for vehicle in self.simulation.model.vehicles:
            sum_car_speed += vehicle.get_speed()
        return sum_car_speed