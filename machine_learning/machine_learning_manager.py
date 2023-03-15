from platform import system

if system() == 'Windows':
    import sys

    sys.path.append('./')
import os
import csv
from library.file_management import FileManagement
from machine_learning.deep_q_learning import MachineLearning


class MachineLearningManager:
    def __init__(self, file_path) -> None:
        self.iterations = []
        self.get_iterations(file_path)
        self.run_iterations()

    def get_iterations(self, file_path):
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            for file_dict in csv_reader:
                self.iterations.append(file_dict)

    def run_iterations(self):
        for iteration in self.iterations:
            self.run_iteration(iteration["Junction"], iteration["SimulationConfig"], iteration["MachineLearningConfig"],iteration["MachineLearningConfigID"])

    def run_iteration(self, junction_file_name, sim_config_file, machine_learning_config_file,machine_learning_config_id):
        junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "junctions",junction_file_name)
        simulation_config_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))),"configurations", "simulation_config", sim_config_file)
        machine_learning_file = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "configurations","machine_learning_config", machine_learning_config_file)
        machine_learning_options = FileManagement().load_ML_configs_from_file(machine_learning_file)
        machine_learning_config = machine_learning_options[int(machine_learning_config_id)]
        print("\n\nMachine Learning with")
        print("Junction:", junction_file_path)
        print("SimConfig:", simulation_config_file_path)
        print("ML:", machine_learning_config.config_id)
        machine_learning = MachineLearning(junction_file_path, simulation_config_file_path, machine_learning_config)
        # machine_learning.train()
