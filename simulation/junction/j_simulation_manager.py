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

from simulation.junction.j_simulation import Simulation


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
        self.light_controlled_path_uids, self.light_path_uids = self.simulation.model.get_traffic_light_controlled_path_uids()

        # TODO: Try combining both and using route_distance_travelled for input oir distance to the traffic light?

        # Inputs / States
        self.features_per_vehicle_state = 4
        self.features_per_traffic_light_state = 0
        self.number_of_tracked_vehicles_per_light_controlled_path = 4
        self.number_of_tracked_vehicles_per_light_path = 1
        self.observation_space_size = self.features_per_vehicle_state * (
                len(self.light_controlled_path_uids) * self.number_of_tracked_vehicles_per_light_controlled_path +
                len(self.light_path_uids) * self.number_of_tracked_vehicles_per_light_path
        ) + self.features_per_traffic_light_state * len(self.simulation.model.lights)

        self.light_controlled_path_uids += self.light_path_uids

        # TODO: Initialize separate boxes by argmax for different inputs
        self.observation_space = Box(0, 50, shape=(1, self.observation_space_size), dtype=float)
        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()
        self.freeze_traffic(15)
        return self.get_state()

    def freeze_traffic(self, n: int = None):
        # TODO: Add randomisation
        if n is None:
            n = random.randint(5, 20)

        for light in self.simulation.model.lights:
            # if random.random() > 0.5:
            light.set_red()

        for step in range(n * self.simulation.model.tick_rate):
            self.simulation.compute_single_iteration()

    def calculate_actions(self):
        # TODO: Sparse actions
        # Avoid do nothing action if not using RNN
        self.action_table = list(itertools.product([-1, 1], repeat=len(self.simulation.model.lights)))
        self.action_table = [action for action in self.action_table if action.count(1) == 1]
        # self.action_table.pop(self.action_table.index(tuple([-1 for _ in self.simulation.model.lights])))
        # self.action_table.pop(self.action_table.index(tuple([1 for _ in self.simulation.model.lights])))
        print(self.action_table)
        # self.action_table = []
        # for action in list(itertools.product([-1, 0, 1], repeat=len(self.simulation.model.lights))):
        #     if action.count(0) >= len(self.simulation.model.lights) - 1:
        #         self.action_table.append(action)
        # self.do_nothing_action_index = self.action_table.index(tuple([0 for _ in range(len(self.simulation.model.lights))]))
        number_of_actions = len(self.action_table)
        return number_of_actions, Discrete(number_of_actions)

    def get_legal_actions(self):
        return list(range(len(self.action_table)))

        # lights = self.simulation.model.lights
        # legal_actions = []
        # for action_index, action in enumerate(self.action_table):
        #     legal = True
        #     for light_index, light in enumerate(lights):
        #         if (
        #                 (action[light_index] == 1 and light.colour == "red") or
        #                 (action[light_index] == -1 and light.colour == "green") or
        #                 action[light_index] == 0
        #         ):
        #             continue
        #         else:
        #             legal = False
        #             break
        #     if legal:
        #         legal_actions.append(action_index)
        # return legal_actions

    def get_illegal_actions(self):
        return [index for index in range(len(self.action_table)) if index not in self.get_legal_actions()]

    def take_action(self, action_index):
        action = self.action_table[action_index]
        for light_index, light in enumerate(self.simulation.model.lights):
            if action[light_index] == 1:
                light.set_green()
            elif action[light_index] == -1:
                light.set_red()
            else:
                continue

    def get_vehicle_state(self, vehicle: Vehicle):
        # x, y = self.simulation.model.get_vehicle_coordinates(vehicle.uid)
        return [
            vehicle.get_route_uid(),
            vehicle.get_route_distance_travelled(),
            vehicle.get_speed(),
            self.simulation.model.get_delay(vehicle.uid)
            # x,
            # y
            # vehicle.wait_time,
            # vehicle.get_length(),
            # vehicle.get_acceleration()
        ]

    def get_traffic_light_state(self, light: TrafficLight):
        return [
            light.get_state(),
            light.time_remaining
            # light.path_uid
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
                path_inputs[self.light_controlled_path_uids.index(path_uid)].append(self.get_vehicle_state(vehicle)) # TODO: use if route_uid is disabled #+ [path_uid])

        # Sort and flatten the inputs by distance travelled
        for index, path_input in enumerate(path_inputs):
            # Sorted adds more weight to the neural inputs of vehicles close to the traffic light
            sorted_path_input = sorted(path_input, key=lambda features: features[0], reverse=True)
            flattened_path_input = list(chain.from_iterable(sorted_path_input))
            path_inputs[index] = flattened_path_input

        for index, path_input in enumerate(path_inputs):
            if index < len(self.light_controlled_path_uids) - len(self.light_path_uids):
                inputs += self.pad_state_input(path_input, self.number_of_tracked_vehicles_per_light_controlled_path)
            else:
                inputs += self.pad_state_input(path_input, self.number_of_tracked_vehicles_per_light_path)
        return np.array(inputs)

    def pad_state_input(self, state_input: list, n: int):
        if len(state_input) > self.features_per_vehicle_state * n:
            state_input = state_input[:self.features_per_vehicle_state * n]
        else:
            state_input += [0.0] * (self.features_per_vehicle_state * n - len(state_input))

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

    def get_state_value(self):
        return sum([self.simulation.model.get_delay(vehicle.uid)**2 for vehicle in self.simulation.model.vehicles if vehicle.get_path_index() == 0])

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

    def get_delays(self):
        return self.simulation.delays