from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')
import os
from library.file_management import FileManagement
from machine_learning.deep_q_learning import MachineLearning

class MachineLearningManager:
    def __init__(self, file_path) -> None:
        self.machine_learning_options = FileManagement().load_ML_configs_from_file(self.machine_learning_config)
        self.iterations = self.get_iteration(file_path)

    def get_iteration(self, file_path):
        pass 
    
    def run_iterations(self):
        for iteration in self.iterations:
            self.run_iteration(iteration["Junction"], iteration["SimulationConfig"], iteration["MachineLearningConfig"], iteration["MAchineLearningConfigID"])
    
    def run_iteration(self, junction_file_name, sim_config_file, machine_learning_config_file, machine_learning_config_id):
        junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "junctions", junction_file_name)
        simulation_config_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))), "configurations", "simulation_config", sim_config_file)
        machine_learning_options = FileManagement().load_ML_configs_from_file(machine_learning_config_file)
        machine_learning_config = machine_learning_options[machine_learning_config_id]
        machine_learning = MachineLearning(junction_file_path, simulation_config_file_path, machine_learning_config)
