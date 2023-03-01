from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from gym import Env
from gym.spaces import Discrete, Box, Dict
import numpy as np
from numpy import mean

from simulation.simulation import Simulation
from simulation.stats import Stats


class Environment(Env):
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        self.simulation.model.setup_fixed_spawning(3)

        # Inputs / States
        self.observation_space_size = 10
        self.observation_space = Box(0, 10, shape=(1, self.observation_space_size), dtype=float)
        self.state = np.asarray(np.zeros(self.observation_space_size)).astype('float32')

        # Actions
        self.action_space = Discrete(3)

        # Iterations
        self.iteration = 0

        # # --------------
        #
        # # State
        self.wait_time = None
        self.wait_time_vehicle_limit = None
        # self.collision = None
        #
        # # Action
        #
        # # Reward
        self.reward = 0
        self.total_reward = 0
        #
        # # -------------
        #
        # self.reset()

    def reset(self):
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        self.simulation.model.setup_fixed_spawning(3)

        self.state = np.asarray(np.zeros(self.observation_space_size)).astype('float32')

        self.iteration = 0

        # # State
        self.wait_time = [0]
        self.wait_time_vehicle_limit = 50
        # self.collision = None
        #
        # # Action
        #
        # # Reward
        self.reward = 0
        self.total_reward = 0

    def take_action(self, action_index):
        penalty = 0
        if action_index == 0:
            pass
        elif action_index == 1:
            if self.simulation.model.get_lights()[0] == "green":
                self.simulation.model.get_lights()[0].set_red()
            else:
                penalty = -10000
        elif action_index == 2:
            if self.simulation.model.get_lights()[1] == "green":
                self.simulation.model.get_lights()[1].set_red()
            else:
                penalty = -10000
        return penalty

    def take_step(self, action_index):
        # Take action
        action_penalty = self.take_action(action_index)
        # Simulate
        self.simulation.compute_single_iteration()

        for vehicle in self.simulation.model.vehicles:
            if vehicle.get_speed() < 5:
                vehicle.add_wait_time(self.simulation.model.tick_time)

            route = self.simulation.model.get_route(vehicle.get_route_uid())
            path = self.simulation.model.get_path(route.get_path_uid(vehicle.get_path_index()))
            if vehicle.get_path_distance_travelled() >= path.get_length():
                if vehicle.get_path_index() + 1 == len(route.get_path_uids()):
                    self.wait_time.append(vehicle.get_wait_time())
                    self.wait_time = self.wait_time[-self.wait_time_vehicle_limit:]

        # Reward
        self.calculate_reward(action_penalty)

        if self.total_reward < -500000:
            done = True
            print(f"Score: {self.total_reward} / Steps: {self.iteration}")
        else:
            done = False

        self.iteration += 1
        state = np.asarray(self.get_state()).astype('float32')

        return state, 1, done

    def get_state(self):
        return np.array(
            [
                self.get_path_occupancy(1),
                self.get_path_wait_time(1),
                self.get_mean_speed(1),
                self.get_path_occupancy(4),
                self.get_path_wait_time(4),
                self.get_mean_speed(4),
                self.simulation.model.get_lights()[0].get_state(),
                self.simulation.model.get_lights()[0].get_time_remaining(),
                self.simulation.model.get_lights()[1].get_state(),
                self.simulation.model.get_lights()[1].get_time_remaining(),
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

    def calculate_reward(self, penalty):
        self.reward = 30 - self.get_mean_wait_time() ** 2 + penalty + (self.iteration / 1000)
        if self.simulation.model.detect_collisions() is not None:
            self.reward -= 5000

        self.total_reward += self.reward

    def get_mean_wait_time(self):
        return mean(self.wait_time)
