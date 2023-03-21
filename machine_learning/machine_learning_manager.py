from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
import csv
from library.file_management import FileManagement

from machine_learning.junction.deep_q_learning import MachineLearning as JunctionMachineLearning
from simulation.junction.simulation_manager import SimulationManager as JunctionSimulationManager

from machine_learning.lane_changing.lc_deep_q_learning import MachineLearning as LaneChangingMachineLearning
from simulation.lane_changing.lc_simulation_manager import SimulationManager as LaneChangingSimulationManager
import time


class MachineLearningManager:
    def __init__(self, file_path) -> None:
        self.training_runs = []
        self.fieldnames = []
        self.output_directory_path = ""
        self.summary_file_path = ""
        self.results_directory_path = ""
        self.machine_learning = None
        self.prepare_files(file_path)
        self.create_summary_file()
        self.run_training_runs()

    def prepare_files(self, file_path):
        self.get_training_runs(file_path)
        self.output_directory_path = (self.get_file_path(["results", (file_path[:-4] + "_RESULTS")]))
        counter = 1
        temp_path = self.output_directory_path
        while os.path.exists(temp_path):
            temp_path = self.output_directory_path + "(" + str(counter) + ")"
            counter += 1
        self.output_directory_path = temp_path
        os.mkdir(self.output_directory_path)
        self.summary_file_path = self.get_file_path([self.output_directory_path, (file_path[:-4] + "_summary_results" + file_path[-4:])])

    def get_training_runs(self, file_path):
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            self.fieldnames = csv_reader.fieldnames
            self.fieldnames += ["Time Taken", "Mean Reward"]
            for file_dict in csv_reader:
                self.training_runs.append(file_dict)

    def run_training_runs(self):
        time_begin = time.perf_counter()
        for run in self.training_runs:
            time_taken, reward = self.run_training_run(run["RunUID"], run["RunType"], run["Junction"], run["SimulationConfig"], run["MachineLearningConfig"], run["MachineLearningConfigID"])
            run.update({"Time Taken": time_taken, "Mean Reward": reward})
            self.save_summary_results(run)
            self.make_directory(run)
        time_taken = time.perf_counter() - time_begin
        print("\n\n================================================\nALL ITERATIONS COMPLETE\n    Total Time: " +
              str(time_taken) + "\n    Total Training Runs: " + str(len(self.training_runs)) + "\n    Results Directory: " + self.output_directory_path +
              "\n================================================")

    def run_training_run(self, run_uid, run_type, junction_file_name, sim_config_file, machine_learning_config_file, machine_learning_config_id):
        # Get file paths for configs
        junction_file_path = self.get_file_path(["junctions", junction_file_name])
        simulation_config_file_path = self.get_file_path(["configurations", "simulation_config", sim_config_file])
        machine_learning_file_path = self.get_file_path(["configurations", "machine_learning_config", machine_learning_config_file])
        machine_learning_config_options = FileManagement().load_ML_configs_from_file(machine_learning_file_path)
        machine_learning_config = machine_learning_config_options[int(machine_learning_config_id)]
        # Initialise simulation
        if run_type.lower() == "junction":
            simulation = JunctionSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
            self.machine_learning = JunctionMachineLearning(simulation, machine_learning_config)
        elif run_type.lower() == "lane changing":
            simulation = LaneChangingSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
            self.machine_learning = LaneChangingMachineLearning(simulation, machine_learning_config)
        else:
            print("ERROR Incompatible Type in config UID:" + str(run_uid))
            exit()
        # Train ML
        print("Running Machine Learning:\n    RunUID: " + str(run_uid) + "\n    Run Type: " + run_type + "\n    Junction: " + junction_file_name + "\n    Simulation Config: "
              + sim_config_file + "\n    Machine Learning Config: " + machine_learning_config_file + "\n    Machine Learning Config ID: "
              + machine_learning_config_id + "\nStarting Training...")
        time_begin = time.perf_counter()
        reward = self.machine_learning.random()
        time_taken = time.perf_counter() - time_begin
        print("\nTraining Complete.\n    Time Taken To Train: " + str(time_taken) + "\n    Reward: " + str(reward) + "\n================================================")
        return time_taken, reward

    def get_file_path(self, path_names):
        file_path = os.path.dirname(os.path.join(os.path.dirname(__file__)))
        for path in path_names:
            file_path = os.path.join(file_path, path)
        return file_path

    def create_summary_file(self):
        with open(self.summary_file_path, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()

    def save_summary_results(self, run):
        with open(self.summary_file_path, "a", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(run)

    def make_directory(self, run):
        results_directory_path = self.get_file_path([self.output_directory_path, ("training_results_run_" + str(run["RunUID"]))])
        os.mkdir(results_directory_path)
        os.mkdir((results_directory_path + "/ml_model_weights"))
        self.machine_learning.save_model_weights((results_directory_path + "/ml_model_weights"), "ml_model_weights")
        self.machine_learning.save_model(results_directory_path, "ml_model")
        with open(results_directory_path + "/training_run_parameters.txt", "a", newline='') as file:
            file.write("This is a summary of the parameters for this Model:")
            for line in run:
                file.write("\n" + line + ": " + str(run[line]))
