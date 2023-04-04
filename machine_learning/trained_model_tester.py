from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
import json
import csv
from statistics import mean, stdev

from simulation.junction.j_simulation_manager import SimulationManager as JunctionSimulationManager
# from simulation.lane_changing.lc_simulation_manager import SimulationManager as LaneChangingSimulationManager

from machine_learning.junction.j_deep_q_learning import MachineLearning as JunctionMachineLearning
# from machine_learning.lane_changing.lc_deep_q_learning import MachineLearning as LaneChangingMachineLearning

import time


class TrainedModelTester:
    def __init__(self, file_path) -> None:
        # MEGAMAINTEST - Add additional data outputs here as required
        self.testing_runs = []
        self.output_directory_path = ""
        self.summary_file_path = ""
        self.prepare_files(file_path)
        self.run_testing_runs()

    def prepare_files(self, file_path: str) -> None:
        """
        The prepare_files function is used to prepare the files for testing, create an output directory where all of
        the results will be stored,and creates a summary file within that directory.
        It takes in a file path and uses it to find all of the testing runs that are associated with it.
        If there is already a folder with that name in results, then an integer will be added to it (e.g. results/my_file_RESULTS(2)).

        :param file_path: Path of the file used to run tests
        :return: None
        """
        self.get_testing_runs(file_path)
        # Create test results director
        self.output_directory_path = (self.get_file_path(["results", (file_path[:-5] + "_TESTED")]))
        counter = 1
        temp_path = self.output_directory_path
        while os.path.exists(temp_path):
            temp_path = self.output_directory_path + "(" + str(counter) + ")"
            counter += 1
        self.output_directory_path = temp_path
        os.mkdir(self.output_directory_path)
        # Create test summary file
        self.summary_file_path = self.get_file_path([self.output_directory_path, (file_path[:-5] + "_test_summary" + file_path[-5:])])

    def get_testing_runs(self, file_path: str) -> None:
        """
        The get_testing_runs function takes in a file path and reads the json file at that location.
        It then appends each run listed in the json file to the testing_runs list.

        :param file_path: Path of the file used to run tests
        :return: None
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)
            for key in file_dict:
                self.testing_runs.append(file_dict[key])

    def run_testing_runs(self) -> None:
        """
        The run_testing_runs function is the main function of the Testing class. It runs all testing runs listed in the
        iteration file, and saves their results to a directory.

        :return: None
        """
        time_begin = time.perf_counter()
        for run in self.testing_runs:
            # MEGAMAINTEST - run_testing_runs must also be passed all parameters from the iteration file.
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
        print("\n\n================================================\nALL ITERATIONS COMPLETE\n    Total Time: " + str(time_taken) + "\n    Total Testing Runs: " + str(len(self.testing_runs)) + "\n    Results Directory: " + self.output_directory_path + "\n================================================")

    # MEGAMAINTEST - add the parameters to this function call and add in functionality as required.
    def run_testing_run(self, run_uid, run_type, junction_file_name, sim_config_file_name, ml_model_file_name, steps):

        print("\n================================================")
        # Create paths to config files.
        junction_file_path = self.get_file_path(["junctions", junction_file_name])
        simulation_config_file_path = self.get_file_path(["configurations", "simulation_config", sim_config_file_name])

        # Initialise and run the simulations for both fixed timings and demand scheduling
        print("Running Machine Learning:\n    RunUID: " + str(run_uid) + "\n    Run Type: " + run_type + "\n    Junction: " + junction_file_name + "\n    Simulation Config: " + sim_config_file + "\n    Steps: " + str(steps) + "\nStarting Testinging...")
        time_begin = time.perf_counter()

        if run_type.lower() == "junction":
            ml_model_model_file_path = self.get_file_path(["machine_learning", "junction", ml_model_file_name])
            simulation_manager = JunctionSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
            machine_learning = JunctionMachineLearning(simulation_manager, machine_learning_config=None)
            machine_learning.test(steps, ml_model_model_file_path)
        elif run_type.lower() == "lane_changing":
            pass
        else:
            print("ERROR Incompatible Type in config UID:" + str(run_uid))
            exit()

        time_taken = time.perf_counter() - time_begin

        print("\nTesting Complete."
              + "\n    Time Taken To Test: " + str(time_taken))

        # Determine results for delay
        delay_mean_average = mean(simulation_manager.simulation.delays)
        delay_standard_deviation = stdev(simulation_manager.simulation.delays)
        delay_maximum = max(simulation_manager.simulation.delays)
        delay_minimum = min(simulation_manager.simulation.delays)
        delay_num_vehicles = len(simulation_manager.simulation.delays)

        # Print results for delay
        print("\n Delay Data:"
              + "\n    Delay Mean Average:" + str(delay_mean_average)
              + "\n    Delay Standard Deviation:" + str(delay_standard_deviation)
              + "\n    Delay Maximum Delay:" + str(delay_maximum)
              + "\n    Delay Minimum Delay: " + str(delay_minimum)
              + "\n    Delay Number Of Vehicles: " + str(delay_num_vehicles))

        # Determine results for backup

        backup_mean_average = {}
        backup_standard_deviation = {}
        backup_maximum = {}
        backup_time = {}

        print("\n Path Backup Data:")
        for path in simulation_manager.simulation.path_backup:

            backup_mean_average[path] = mean(simulation_manager.simulation.path_backup[path])
            backup_standard_deviation[path] = stdev(simulation_manager.simulation.path_backup[path])
            backup_maximum[path] = max(simulation_manager.simulation.path_backup[path])
            backup_time[path] = 0
            if path in simulation_manager.simulation.path_backup_total:
                backup_time[path] = simulation_manager.simulation.path_backup_total[path]

            # Print results for backup
            print("\n    Path " + str(path) + ": "
                  + "\n        Backup Mean Average:" + str(backup_mean_average[path])
                  + "\n        Backup Standard Deviation:" + str(backup_standard_deviation[path])
                  + "\n        Backup Maximum Delay:" + str(backup_maximum[path])
                  + "\n        Backup Time:" + str(backup_time[path]))

        return time_taken, delay_mean_average, delay_standard_deviation, delay_maximum, delay_minimum, delay_num_vehicles, simulation_manager.simulation.delays, backup_mean_average, backup_standard_deviation, backup_maximum, backup_time, simulation_manager.simulation.path_backup

    def get_file_path(self, path_names: list) -> str:
        """
        The get_file_path function takes a list of folders / file names and returns a concatenated absolute file path.
        strings.

        :param path_names: list: Specify the path to a file
        :return: The path to the file
        """
        file_path = os.path.dirname(os.path.join(os.path.dirname(__file__)))
        for path in path_names:
            file_path = os.path.join(file_path, path)
        return file_path

    def make_results_directory(self, run: dict) -> None:
        """
        The make_results_directory function creates a directory for the results of each run.
        It also writes the parameters used in that run to a text file, and writes the delay and backup results to csv
        files.

        :param run: dict: Pass the dictionary of parameters to the function
        :return: None
        """
        # Make results director
        results_directory_path = self.get_file_path([self.output_directory_path, ("run_" + str(run["RunUID"]))])
        os.mkdir(results_directory_path)
        with open(results_directory_path + "/testing_run_parameters.txt", "a", newline='') as file:
            file.write("This is a summary of the parameters for this Model:")
            for line in run:
                file.write("\n" + line + ": " + str(run[line]))

        # Write raw delay results
        with open(results_directory_path + "/testing_run_delay_results.csv", 'w') as file:
            write = csv.writer(file)
            for value in run["Delay"]:
                write.writerow([value])

        # Write raw backup results
        with open(results_directory_path + "/testing_run_backup_results.csv", 'w') as file:
            write = csv.writer(file)
            for i in range(len(run["Backup"][list(run["Backup"].keys())[0]])):
                values = []
                for path in run["Backup"]:
                    values.append(run["Backup"][path][i])
                write.writerow(values)

