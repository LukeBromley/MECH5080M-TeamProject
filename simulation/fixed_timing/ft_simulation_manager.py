from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('../')

import os

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
        self.actions = [1, 2]
        self.action_duration = 100

        # Current Action
        self.current_action_index = 0
        self.action_duration_counter = 0

        self.reset()

    def calculate_possible_actions(self):
        number_of_lights = len(self.simulation.model.lights)
        number_of_possible_actions = 2**(number_of_lights)

        print("--- Possible actions ---")

        uid_strings = ""
        for light in self.simulation.model.lights:
            uid_string = str(light.uid)
            while len(uid_string) < 7:
                uid_string += " "
            uid_strings += uid_string
        print("Index  ", uid_strings)

        for index in range(number_of_possible_actions):
            bin = format(index, '0' + str(number_of_lights) + 'b')
            bin_string = ""
            for bit in bin:
                bin_string += bit + "      "
            index_string = str(index)
            while len(index_string) < 7:
                index_string += " "

            print(index_string, bin_string)

        return number_of_lights, number_of_possible_actions

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

    def run(self):
        for i in range(10000):
            self.take_action(self.actions[self.current_action_index])

            self.simulation.run_single_iteration()

            sleep(0.1)

            self.action_duration_counter += 1
            if self.action_duration_counter >= self.action_duration:
                self.action_duration_counter = 0
                self.current_action_index += 1
                if self.current_action_index >= len(self.actions):
                    self.current_action_index = 0

    def get_delays(self):
        return self.simulation.delays

if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations/simulation_config", "cross_road.config")

    # Settings
    scale = 200

    # Visualiser Init
    visualiser = JunctionVisualiser()

    simulation_manager = SimulationManager(junction_file_path, configuration_file_path, visualiser_update_function=visualiser.update)

    # Visualiser Setup
    visualiser.define_main(simulation_manager.run)
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)
    #
    # Run Simulation
    visualiser.open()
