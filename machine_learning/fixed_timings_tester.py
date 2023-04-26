from functools import partial
from platform import system

from gui.junction_visualiser import JunctionVisualiser

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

            time_taken, number_of_vehicles_spawned,\
            delay_mean_average, delay_standard_deviation, delay_maximum, delay_minimum, delay_num_vehicles, delays, \
            backup_mean_average, backup_standard_deviation, backup_maximum, backup_time, backup, \
            kinetic_energy_waste_mean_average, kinetic_energy_waste_standard_deviation, kinetic_energy_waste_maximum, kinetic_energy_waste_minimum, kinetic_energy = self.run_testing_run(run["RunUID"], run["RunType"], run["Junction"], run["SimulationConfig"], run["Steps"], run["Actions"], run["ActionDurations"], run["ActionPaths"])

            # MEGAMAINTEST - make sure any results are returned here and 'run' is updated with them in dictionary format.
            run.update({"Time Taken": time_taken,
                        "Number Of Vehicles Spawned": number_of_vehicles_spawned,
                        "Delay Mean Average": delay_mean_average,
                        "Delay Standard Deviation": delay_standard_deviation,
                        "Delay Maximum": delay_maximum,
                        "Delay Minimum": delay_minimum,
                        "Delay Number Of Cars": delay_num_vehicles,
                        "Backup Mean Average": backup_mean_average,
                        "Backup Standard Deviation": backup_standard_deviation,
                        "Backup Maximum": backup_maximum,
                        "Backup Time": backup_time,
                        "Kinetic Energy Waste Average": kinetic_energy_waste_mean_average,
                        "Kinetic Energy Waste Standard Deviation": kinetic_energy_waste_standard_deviation,
                        "Kinetic Energy Waste Maximum": kinetic_energy_waste_maximum,
                        "Kinetic Energy Waste Minimum": kinetic_energy_waste_minimum,
                        })
            self.make_results_directory(run, delays, backup, kinetic_energy)
        time_taken = time.perf_counter() - time_begin
        # MEGAMAINTEST - Add any results you want printed to terminal as required.
        print("\n\n================================================\nALL ITERATIONS COMPLETE\n    Total Time: " + str(time_taken) + "\n    Total Testing Runs: " + str(len(self.testing_runs)) + "\n    Results Directory: " + self.output_directory_path + "\n================================================")

    # MEGAMAINTEST - add the parameters to this function call and add in functionality as required.
    def run_testing_run(self, run_uid, run_type, junction_file_name, sim_config_file, steps, actions, action_durations, action_paths):

        """
        The run_testing_run function is used to run a single testing run using the parameters specified in the iteration
        file. It also displays the results and progress of the test run in the terminal.

        :param run_uid: Unique ID of the run in the iteration file
        :param run_type: Determine whether the simulation should be run with fixed timings or demand scheduling
        :param junction_file_name: The file path of the junction to use
        :param sim_config_file: The file path of the configuration file to use for the simulation
        :param steps: Determine how many steps the simulation will run for
        :param actions: A list of actions that can be taken by the lights
        :param action_durations: Specify the duration of each action
        :param action_paths: Specify which paths need to be sensed for demand scheduling
        :return: A tuple of results
        """
        print("\n================================================")
        # Create paths to config files.
        junction_file_path = self.get_file_path(["junctions", junction_file_name])
        simulation_config_file_path = self.get_file_path(["configurations", "simulation_config", sim_config_file])

        # Initialise and run the simulations for both fixed timings and demand scheduling
        print("Running Machine Learning:\n    RunUID: " + str(run_uid) + "\n    Run Type: " + run_type + "\n    Junction: " + junction_file_name + "\n    Simulation Config: " + sim_config_file + "\n    Steps: " + str(steps) + "\nStarting Testinging...")
        time_begin = time.perf_counter()

        if run_type.lower() == "fixed timings":
            simulation_manager = FixedTimingSimulationManager(junction_file_path, simulation_config_file_path)
            simulation_manager.run(steps, actions, action_durations)
        elif run_type.lower() == "demand scheduling":
            # # Visualiser Setup
            # visualiser = JunctionVisualiser()
            # visualiser_update_function = visualiser.update
            #
            # simulation_manager = DemandSchedulingSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=visualiser_update_function)
            #
            # visualiser.define_main(partial(simulation_manager.run, steps, actions, action_durations, action_paths))
            # visualiser.load_junction(junction_file_path)
            # visualiser.set_scale(30)
            # #
            # # Run Simulation
            # visualiser.open()
            simulation_manager = DemandSchedulingSimulationManager(junction_file_path, simulation_config_file_path)
            simulation_manager.run(steps, actions, action_durations, action_paths)
        else:
            print("ERROR Incompatible Type in config UID:" + str(run_uid))
            exit()

        time_taken = time.perf_counter() - time_begin

        print("\nTesting Complete."
              + "\n    Time Taken To Test: " + str(time_taken))

        number_of_vehicles_spawned = simulation_manager.simulation.number_of_vehicles_spawned

        print("\n Number Vehicles Spawned:" + str(number_of_vehicles_spawned))

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
            backup_time[path] = simulation_manager.simulation.path_backup_total[path]

            # Print results for backup
            print("\n    Path " + str(path) + ": "
                  + "\n        Backup Mean Average:" + str(backup_mean_average[path])
                  + "\n        Backup Standard Deviation:" + str(backup_standard_deviation[path])
                  + "\n        Backup Maximum Delay:" + str(backup_maximum[path])
                  + "\n        Backup Time:" + str(backup_time[path]))

        # Determine results for kinetic energy waste

        kinetic_energy_waste = simulation_manager.simulation.kinetic_energy_waste.values()
        kinetic_energy_waste_mean_average = mean(kinetic_energy_waste)
        kinetic_energy_waste_standard_deviation = stdev(kinetic_energy_waste)
        kinetic_energy_waste_maximum = max(kinetic_energy_waste)
        kinetic_energy_waste_minimum = min(kinetic_energy_waste)

        # Print results for kinetic energy waste
        print("\n Kinetic Energy Data:"
              + "\n    Kinetic Energy Waste Mean Average:" + str(kinetic_energy_waste_mean_average)
              + "\n    Kinetic Energy Waste Standard Deviation:" + str(kinetic_energy_waste_standard_deviation)
              + "\n    Kinetic Energy Waste Maximum Delay:" + str(kinetic_energy_waste_maximum)
              + "\n    Kinetic Energy Waste Minimum Delay: " + str(kinetic_energy_waste_minimum))

        return time_taken, number_of_vehicles_spawned, \
            delay_mean_average, delay_standard_deviation, delay_maximum, delay_minimum, delay_num_vehicles, simulation_manager.simulation.delays, \
            backup_mean_average, backup_standard_deviation, backup_maximum, backup_time, simulation_manager.simulation.path_backup, \
            kinetic_energy_waste_mean_average, kinetic_energy_waste_standard_deviation, kinetic_energy_waste_maximum, kinetic_energy_waste_minimum, simulation_manager.simulation.kinetic_energy


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

    def make_results_directory(self, run: dict, delays, backup, kinetic_energy) -> None:
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

        with open(results_directory_path + "/testing_run_parameters.json", "a", newline='') as file:
            json.dump(run, file)

        # Write raw delay results
        with open(results_directory_path + "/testing_run_delay_results.csv", 'w') as file:
            write = csv.writer(file)
            for value in delays:
                write.writerow([value])

        # Write raw backup results
        with open(results_directory_path + "/testing_run_backup_results.csv", 'w') as file:
            write = csv.writer(file)
            for i in range(len(backup[list(backup.keys())[0]])):
                values = []
                for path in backup:
                    values.append(backup[path][i])
                write.writerow(values)

        # Write raw kinetic energy results
        with open(results_directory_path + "/testing_run_kinetic_energy_results.csv", 'w') as file:
            write = csv.writer(file)

            kinetic_energy = kinetic_energy.values()

            max_len = 0
            for vehicle_kinetic_energy in kinetic_energy:
                if max_len < len(vehicle_kinetic_energy):
                    max_len = len(vehicle_kinetic_energy)

            for i in range(max_len):
                values = []
                for vehicle_kinetic_energy in kinetic_energy:
                    if i < len(vehicle_kinetic_energy):
                        values.append(vehicle_kinetic_energy[i])
                write.writerow(values)
