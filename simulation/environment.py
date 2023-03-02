from platform import system
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
        # self.simulation.model.setup_fixed_spawning(3)

        # Actions
        self.number_of_possible_actions, self.action_space = self.calculate_actions()

        # Metrics
        self.wait_time = None
        self.wait_time_vehicle_limit = None

        # Inputs / States
        self.observation_space_size = 10
        self.observation_space = Box(0, 10, shape=(1, self.observation_space_size), dtype=float)

        self.reset()

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        # simulation.model.setup_fixed_spawning(3)
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
        if action_index == 0:
            pass
        elif action_index == 1:
            light = self.simulation.model.lights[0]
            if light.colour == "green":
                light.set_red()
        elif action_index == 2:
            light = self.simulation.model.lights[1]
            if light.colour == "green":
                light.set_red()
        elif action_index == 3:
            light = self.simulation.model.lights[0]
            if light.colour == "red":
                light.set_green()
        elif action_index == 4:
            light = self.simulation.model.lights[1]
            if light.colour == "red":
                light.set_green()
        return 0

    def compute_simulation_metrics(self):
        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < 5:
                vehicle.add_wait_time(self.simulation.model.tick_time)

            route = self.simulation.model.get_route(vehicle.get_route_uid())
            path = self.simulation.model.get_path(route.get_path_uid(vehicle.get_path_index()))
            if vehicle.get_path_distance_travelled() >= path.get_length():
                if vehicle.get_path_index() + 1 == len(route.get_path_uids()):
                    self.wait_time.append(vehicle.get_wait_time())
                    self.wait_time = self.wait_time[-self.wait_time_vehicle_limit:]

    def calculate_reward(self, penalty):
        reward = 30 - self.get_mean_wait_time() ** 2 + penalty
        if len(self.simulation.model.detect_collisions()) > 0:
            reward -= 5000
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

    def get_mean_wait_time(self):
        return mean(self.wait_time)

    def get_lights(self):
        return self.simulation.model.get_lights()