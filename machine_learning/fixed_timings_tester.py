from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
import json
import csv
from statistics import mean, stdev

from simulation.fixed_timing.ft_simulation_manager import SimulationManager as FixedTimingSimulationManager
from simulation.fixed_timing.ds_simulation_manager import SimulationManager as DemandSchedulingSimulationManager

import time


class FixedTimingsTester:
    def __init__(self, file_path) -> None:
        # MEGAMAINTEST - Add additional data outputs here as required
        self.output_fields = ["Time Taken", "Mean Reward"]
        self.training_runs = []
        self.fieldnames = []
        self.output_directory_path = ""
        self.summary_file_path = ""
        self.results_directory_path = ""
        self.machine_learning = None
        self.prepare_files(file_path)
        self.run_testing_runs()

    def prepare_files(self, file_path):
        self.get_training_runs(file_path)
        self.output_directory_path = (self.get_file_path(["results", (file_path[:-5] + "_TESTED")]))
        counter = 1
        temp_path = self.output_directory_path
        while os.path.exists(temp_path):
            temp_path = self.output_directory_path + "(" + str(counter) + ")"
            counter += 1
        self.output_directory_path = temp_path
        os.mkdir(self.output_directory_path)
        self.summary_file_path = self.get_file_path([self.output_directory_path, (file_path[:-5] + "_tested_summary" + file_path[-5:])])

    def get_training_runs(self, file_path):
        with open(file_path, "r") as file:
            file_dict = json.load(file)
            for key in file_dict:
                self.training_runs.append(file_dict[key])

    def run_testing_runs(self):
        time_begin = time.perf_counter()
        for run in self.training_runs:
            # MEGAMAINTEST - run_training_runs must also be passed all parameters from the iteration file.
            time_taken, delay_mean_average, delay_standard_deviation, delay_maximum, delay_minimum, delay_num_vehicles, delays, \
            backup_mean_average, backup_standard_deviation, backup_maximum, backup_time, backup = self.run_testing_run(run["RunUID"], run["RunType"], run["Junction"], run["SimulationConfig"], run["Steps"], run["Actions"], run["ActionDurations"], run["ActionPaths"])
            # MEGAMAINTEST - make sure any results are returned here and 'run' is updated with them in dictionary format.
            run.update({"Time Taken": time_taken,
                        "Delay Mean Average": delay_mean_average,
                        "Delay Standard Deviation": delay_standard_deviation,
                        "Delay Maximum": delay_maximum,
                        "Delay Minimum": delay_minimum,
                        "Delay Number Of Cars": delay_num_vehicles,
                        "Delay": delays,
                        "Backup Mean Average": backup_mean_average,
                        "Backup Standard Deviation": backup_standard_deviation,
                        "Backup Maximum": backup_maximum,
                        "Backup Time": backup_time,
                        "Backup": backup
                        })
            self.make_results_directory(run)
        time_taken = time.perf_counter() - time_begin
        # MEGAMAINTEST - Add any results you want printed to terminal as required.
        print("\n\n================================================\nALL ITERATIONS COMPLETE\n    Total Time: " + str(time_taken) + "\n    Total Training Runs: " + str(len(self.training_runs)) + "\n    Results Directory: " + self.output_directory_path + "\n================================================")

    # MEGAMAINTEST - add the parameters to this function call and add in functionality as required.
    def run_testing_run(self, run_uid, run_type, junction_file_name, sim_config_file, steps, actions, action_durations, action_paths):
        print("\n================================================")
        # Create paths to config files.
        junction_file_path = self.get_file_path(["junctions", junction_file_name])
        simulation_config_file_path = self.get_file_path(["configurations", "simulation_config", sim_config_file])

        # Test FT
        print("Running Machine Learning:\n    RunUID: " + str(run_uid) + "\n    Run Type: " + run_type + "\n    Junction: " + junction_file_name + "\n    Simulation Config: " + sim_config_file + "\n    Steps: " + str(steps) + "\nStarting Training...")
        time_begin = time.perf_counter()

        # Initialise simulation with either junction or lane changing set up.
        if run_type.lower() == "fixed timings":
            simulation_manager = FixedTimingSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
            simulation_manager.run(steps, actions, action_durations)
        elif run_type.lower() == "demand scheduling":
            simulation_manager = DemandSchedulingSimulationManager(junction_file_path, simulation_config_file_path,visualiser_update_function=None)
            simulation_manager.run(steps, actions, action_durations, action_paths)
        else:
            print("ERROR Incompatible Type in config UID:" + str(run_uid))
            exit()

        time_taken = time.perf_counter() - time_begin

        delay_mean_average = mean(simulation_manager.simulation.delays)
        delay_standard_deviation = stdev(simulation_manager.simulation.delays)
        delay_maximum = max(simulation_manager.simulation.delays)
        delay_minimum = min(simulation_manager.simulation.delays)
        delay_num_vehicles = len(simulation_manager.simulation.delays)

        print("\nTraining Complete."
              + "\n    Time Taken To Train: " + str(time_taken))

        print("\n Delay Data:"
              + "\n    Delay Mean Average:" + str(delay_mean_average)
              + "\n    Delay Standard Deviation:" + str(delay_standard_deviation)
              + "\n    Delay Maximum Delay:" + str(delay_maximum)
              + "\n    Delay Minimum Delay: " + str(delay_minimum)
              + "\n    Delay Number Of Vehicles: " + str(delay_num_vehicles))

        print("\n Path Backup Data:")

        backup_mean_average = {}
        backup_standard_deviation = {}
        backup_maximum = {}
        backup_time = {}

        for path in simulation_manager.simulation.path_backup:

            backup_mean_average[path] = mean(simulation_manager.simulation.path_backup[path])
            backup_standard_deviation[path] = stdev(simulation_manager.simulation.path_backup[path])
            backup_maximum[path] = max(simulation_manager.simulation.path_backup[path])
            backup_time[path] = 0
            if path in simulation_manager.simulation.path_backup_total:
                backup_time[path] = simulation_manager.simulation.path_backup_total[path]

            print("\n    Path " + str(path) + ": "
                  + "\n        Backup Mean Average:" + str(backup_mean_average[path])
                  + "\n        Backup Standard Deviation:" + str(backup_standard_deviation[path])
                  + "\n        Backup Maximum Delay:" + str(backup_maximum[path])
                  + "\n        Backup Time:" + str(backup_time[path]))

        return time_taken, delay_mean_average, delay_standard_deviation, delay_maximum, delay_minimum, delay_num_vehicles, simulation_manager.simulation.delays, backup_mean_average, backup_standard_deviation, backup_maximum, backup_time, simulation_manager.simulation.path_backup

    def get_file_path(self, path_names):
        file_path = os.path.dirname(os.path.join(os.path.dirname(__file__)))
        for path in path_names:
            file_path = os.path.join(file_path, path)
        return file_path

    def make_results_directory(self, run):
        results_directory_path = self.get_file_path([self.output_directory_path, ("run_" + str(run["RunUID"]))])
        os.mkdir(results_directory_path)
        with open(results_directory_path + "/training_run_parameters.txt", "a", newline='') as file:
            file.write("This is a summary of the parameters for this Model:")
            for line in run:
                file.write("\n" + line + ": " + str(run[line]))

        with open(results_directory_path + "/training_run_delay_results.csv", 'w') as file:
            write = csv.writer(file)
            for value in run["Delay"]:
                write.writerow([value])

        with open(results_directory_path + "/training_run_backup_results.csv", 'w') as file:
            write = csv.writer(file)
            for i in range(len(run["Backup"][list(run["Backup"].keys())[0]])):
                values = []
                for path in run["Backup"]:
                    values.append(run["Backup"][path][i])
                write.writerow(values)