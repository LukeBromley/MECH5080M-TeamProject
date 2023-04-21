from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('../')

import os
from functools import partial
from time import sleep

from simulation.junction.j_simulation import Simulation
from gui.junction_visualiser import JunctionVisualiser


class SimulationManager:
    def __init__(self, junction_file_path, config_file_path, visualiser_update_function=None):
        self.junction_file_path = junction_file_path
        self.config_file_path = config_file_path
        self.visualiser_update_function = visualiser_update_function

        # Simulations
        self.simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)

        # Actions
        self.number_of_lights, self.number_of_possible_actions = self.calculate_possible_actions()
        self.actions = []
        self.action_paths = []
        self.action_duration = []
        self.demand = []

        # Current Action
        self.current_action_index = 0
        self.action_duration_counter = 0
        self.empty_action_duration_counter = 0

        self.reset()

    def calculate_possible_actions(self):
        number_of_lights = len(self.simulation.model.lights)
        number_of_possible_actions = 2 ** (number_of_lights)
        return number_of_lights, number_of_possible_actions

    def print_possible_actions(self):
        print("--- Possible actions ---")

        uid_strings = ""
        for light in self.simulation.model.lights:
            uid_string = str(light.uid)
            while len(uid_string) < 7:
                uid_string += " "
            uid_strings += uid_string
        print("Index  ", uid_strings)

        for index in range(self.number_of_possible_actions):
            bin = format(index, '0' + str(self.number_of_lights) + 'b')
            bin_string = ""
            for bit in bin:
                bin_string += bit + "      "
            index_string = str(index)
            while len(index_string) < 7:
                index_string += " "

            print(index_string, bin_string)

    def create_simulation(self):
        simulation = Simulation(self.junction_file_path, self.config_file_path, self.visualiser_update_function)
        return simulation

    def reset(self):
        self.simulation = self.create_simulation()

    def take_action(self, action):
        bin = format(action, '0' + str(self.number_of_lights) + 'b')
        for index, light in enumerate(self.simulation.model.lights):
            if bin[index] == "0":
                light.set_red()
            else:
                light.set_green()

    def get_lights(self):
        return self.simulation.model.get_lights()

    def run(self, number_of_iterations, actions, action_duration, action_paths, visualiser_delay=False):
        self.actions = actions
        self.action_duration = action_duration
        self.action_paths = action_paths

        for i in range(number_of_iterations):
            self.take_action(self.actions[self.current_action_index])

            self.simulation.run_single_iteration()

            if visualiser_delay:
                sleep(0.01)

            self.simulation.collision = self.simulation.model.detect_collisions()

            self.check_demand()

            self.action_duration_counter += 1
            if self.action_duration_counter >= self.action_duration[self.current_action_index]:
                demand = self.check_current_demand()
                if demand and self.action_duration_counter >= 200:
                    pass
                else:
                    self.action_duration_counter = 0
                    self.empty_action_duration_counter = 0
                    self.demand_increment_action()
            elif self.action_duration_counter >= 30:
                demand = self.check_current_demand()
                if not demand and len(self.demand) > 0:
                    self.empty_action_duration_counter += 1
                    if self.empty_action_duration_counter >= 20:
                        self.empty_action_duration_counter = 0
                        self.action_duration_counter = 0
                        self.demand_increment_action()

    def check_demand(self):
        for action_index, path_uids in enumerate(self.action_paths):
            if action_index not in self.demand:
                for path_uid in path_uids:
                    if path_uid not in self.action_paths[self.current_action_index]:
                        vehicles = self.simulation.model.get_vehicles_on_path(path_uid)
                        if len(vehicles) > 0:
                            self.demand.append(action_index)

    def check_current_demand(self):
        demand = False
        for path_uid in self.action_paths[self.current_action_index]:
            vehicles = self.simulation.model.get_vehicles_on_path(path_uid)
            if len(vehicles) > 0:
                demand = True
        return demand

    def demand_increment_action(self):
        if len(self.demand) > 0:
            self.current_action_index = self.demand[0]
            self.demand.pop(0)
        else:
            self.increment_action()

    def increment_action(self):
        self.current_action_index += 1
        if self.current_action_index >= len(self.actions):
            self.current_action_index = 0


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "scale_library_pub_junction.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations/simulation_config", "demand_mean_12.config")

    # Settings
    scale = 30

    # Visualiser Init
    visualiser = JunctionVisualiser()

    disable_visualiser = False

    if disable_visualiser:
        simulation_manager = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function=None)
        simulation_manager.run(1000, [35, 56, 22], [150, 150, 150], [[7, 8], [10, 11], [13, 14]], visualiser_delay=False)
    else:
        simulation_manager = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function=visualiser.update)
        # Visualiser Setup
        visualiser.define_main(partial(simulation_manager.run, 10000, [35, 56, 22], [150, 150, 150], [[7, 8], [10, 11], [13, 14]], visualiser_delay=False))
        visualiser.load_junction(junction_file_path)
        visualiser.set_scale(scale)

        # Run Simulation
        visualiser.open()
