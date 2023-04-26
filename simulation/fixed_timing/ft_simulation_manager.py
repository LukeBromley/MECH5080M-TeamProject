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
        self.actions = [2, 0, 1, 0]
        self.action_duration = [150, 30, 150, 30]
        self.intermdiary_action = False
        self.intermdiary_action_counter = 0

        # Current Action
        self.current_action_index = 0
        self.action_duration_counter = 0

        self.reset()

    def calculate_possible_actions(self):
        number_of_lights = len(self.simulation.model.lights)
        number_of_possible_actions = 2**(number_of_lights)
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
        if not self.intermdiary_action:
            bin = format(action, '0' + str(self.number_of_lights) + 'b')
            for index, light in enumerate(self.simulation.model.lights):
                if bin[index] == "0":
                    light.set_red()
                else:
                    light.set_green()
        else:
            for index, light in enumerate(self.simulation.model.lights):
                light.set_red()

    def get_lights(self):
        return self.simulation.model.get_lights()

    def run(self, number_of_iterations, actions, action_duration, visualiser_delay=False):
        self.actions = actions
        self.action_duration = action_duration

        for i in range(number_of_iterations):
            self.take_action(self.actions[self.current_action_index])

            self.simulation.run_single_iteration()

            if visualiser_delay:
                sleep(0.03)

            self.simulation.collision = self.simulation.model.detect_collisions()

            if not self.intermdiary_action:
                self.intermdiary_action_counter = 0
                self.action_duration_counter += 1
                if self.action_duration_counter >= self.action_duration[self.current_action_index]:
                    self.action_duration_counter = 0
                    self.current_action_index += 1
                    if self.current_action_index >= len(self.actions):
                        self.current_action_index = 0
                    self.intermdiary_action = True
            else:
                self.intermdiary_action_counter += 1
                if self.intermdiary_action_counter > 30:
                    self.intermdiary_action = False


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "simple_X_junction.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations/simulation_config/final_testing/even_spawning/autonomous/seed_997415346", "30.0cpm.config")

    # Settings
    scale = 50

    # Visualiser Init
    visualiser = JunctionVisualiser()

    simulation_manager = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function=visualiser.update)  # visualiser.update
    simulation_manager.print_possible_actions()

    # Visualiser Setup
    visualiser.define_main(partial(simulation_manager.run, 4500, [2, 1, 8, 4], [300, 300, 300], visualiser_delay=False))
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()
