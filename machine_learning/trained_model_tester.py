from platform import system

if system() == 'Windows':
    import sys
    sys.path.append('./')

import os
import csv

from machine_learning.junction.j_deep_q_learning import MachineLearning as JunctionMachineLearning
from simulation.junction.j_simulation_manager import SimulationManager as JunctionSimulationManager

from machine_learning.lane_changing.lc_deep_q_learning import MachineLearning as LaneChangingMachineLearning
from simulation.lane_changing.lc_simulation_manager import SimulationManager as LaneChangingSimulationManager
import time


class TrainedModelTester:
    def __init__(self, file_path) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets up all the variables that will be used by other functions in this class.
        The file_path parameter is a string containing the path to a CSV file with training run data.

        :param file_path: Create the output directory and results directory
        """
        # MEGAMAINTEST - Add additional data outputs here as required
        self.output_fields = ["Time Taken", "Mean Reward"]
        self.training_runs = []
        self.fieldnames = []
        self.output_directory_path = ""
        self.summary_file_path = ""
        self.results_directory_path = ""
        self.machine_learning = None
        self.prepare_files(file_path)
        self.create_summary_file()
        self.run_testing_runs()

    def prepare_files(self, file_path):
        """
        The prepare_files function is used to create a new directory in the results folder, and then creates a summary file
        in that directory. The name of the new directory will be based on the name of the input file.
        If there is already a folder with that name in results, then an integer will be added to it (e.g. results/my_file_RESULTS(2)).
        The summary file's path will also include this integer if necessary.

        :param file_path: Get the file path of the training runs
        """
        self.get_training_runs(file_path)
        self.output_directory_path = (self.get_file_path(["results", (file_path[:-4] + "_TESTED")]))
        counter = 1
        temp_path = self.output_directory_path
        while os.path.exists(temp_path):
            temp_path = self.output_directory_path + "(" + str(counter) + ")"
            counter += 1
        self.output_directory_path = temp_path
        os.mkdir(self.output_directory_path)
        self.summary_file_path = self.get_file_path([self.output_directory_path, (file_path[:-4] + "_tested_summary" + file_path[-4:])])

    def get_training_runs(self, file_path):
        """
        Takes a file path as an argument and reads the csv file at that location.
        It then creates a list of dictionaries, where each dictionary is one row in the csv file.
        The function also adds to the fieldnames attribute of this class, which will be used later when writing to a new csv.

        :param file_path: The path to the csv.
        """
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            self.fieldnames = csv_reader.fieldnames
            self.fieldnames += self.output_fields  # Adds the result headings to fieldnames
            for file_dict in csv_reader:
                self.training_runs.append(file_dict)

    def run_testing_runs(self):
        time_begin = time.perf_counter()
        for run in self.training_runs:
            # MEGAMAINTEST - run_training_runs must also be passed all parameters from the iteration file.
            time_taken, rewards = self.run_testing_run(run["RunUID"], run["RunType"], run["ControlMethod"], run["Junction"], run["SimulationConfig"], run["ModelFilePath"], run["Episodes"])
            # MEGAMAINTEST - make sure any results are returned here and 'run' is updated with them in dictionary format.
            run.update({"Time Taken": time_taken, "Rewards": rewards})
            self.save_summary_results(run)
            self.make_results_directory(run)
        time_taken = time.perf_counter() - time_begin
        # MEGAMAINTEST - Add any results you want printed to terminal as required.
        print("\n\n================================================\nALL ITERATIONS COMPLETE\n    Total Time: " + str(time_taken) + "\n    Total Training Runs: " + str(len(self.training_runs)) + "\n    Results Directory: " + self.output_directory_path + "\n================================================")

    # MEGAMAINTEST - add the parameters to this function call and add in functionality as required.
    def run_testing_run(self, run_uid, run_type, run_control_method, junction_file_name, sim_config_file, model_file_path, episodes):
        """
        The run_training_run function is used to run a single training run of the machine learning algorithm.

        :param self: Refer to the object that is calling the function
        :param run_uid: Identify the run in the database
        :param run_type: Determine which type of simulation to run, either a junction or lane changing
        :param run_control_method:
        :param junction_file_name: Load the junction file from the junctions folder
        :param sim_config_file: Load the simulation config file
        :param model_file_path: Specify the path to the model file
        :param episodes: Determine how many episodes the machine learning algorithm should run for
        :return: A tuple of the time taken to train and the reward
        """

        print("\n================================================")
        # Create paths to config files.
        junction_file_path = self.get_file_path(["junctions", junction_file_name])
        simulation_config_file_path = self.get_file_path(["configurations", "simulation_config", sim_config_file])
        machine_learning_model_file_path = self.get_file_path([model_file_path])
        # Initialise simulation with either junction or lane changing set up.
        if run_control_method.lower() == "machine learning":
            if run_type.lower() == "junction":
                simulation = JunctionSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
                self.machine_learning = JunctionMachineLearning(simulation, machine_learning_config=None)
            elif run_type.lower() == "lane changing":
                simulation = LaneChangingSimulationManager(junction_file_path, simulation_config_file_path, visualiser_update_function=None)
                self.machine_learning = LaneChangingMachineLearning(simulation, machine_learning_config=None)
            else:
                print("ERROR Incompatible Type in config UID:" + str(run_uid))
                exit()
            # Train ML
            print("Running Machine Learning:\n    RunUID: " + str(run_uid) + "\n    Run Type: " + run_type + "\n    Junction: " + junction_file_name + "\n    Simulation Config: " + sim_config_file + "\n    Model File Path: " + model_file_path + "\n    Episodes: " + episodes + "\nStarting Training...")
            time_begin = time.perf_counter()
            # MEGAMAINTEST - change to ML method required and return all results data.
            rewards = self.machine_learning.test(machine_learning_model_file_path, int(episodes))
            time_taken = time.perf_counter() - time_begin
            print("\nTraining Complete.\n    Time Taken To Train: " + str(time_taken) + "\n    Reward: " + str(rewards) )
            return time_taken, rewards

    def get_file_path(self, path_names):
        """
        The get_file_path function takes a list of strings as an argument.
        It then uses the os module to join the file path with each string in the list,
        and returns that joined file path.

        :param path_names: Specify the file path
        :return: The file path of the given argument
        """
        file_path = os.path.dirname(os.path.join(os.path.dirname(__file__)))
        for path in path_names:
            file_path = os.path.join(file_path, path)
        return file_path

    def create_summary_file(self):
        """
        The create_summary_file function creates a new csv file with the name of the summary_file_path variable.
        The function then writes a header row to that file using the fieldnames variable as column headers.

        :return: A csv file with the headers
        """
        with open(self.summary_file_path, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()

    def save_summary_results(self, run):
        """
        The save_summary_results function takes a run dictionary as an argument and appends it to the summary file.
        The function opens the summary file in append mode, creates a DictWriter object with fieldnames equal to self.fieldnames,
        and writes the row corresponding to the last run.

        :param run: Write the results of this run to a csv file
        """
        with open(self.summary_file_path, "a", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(run)

    def make_results_directory(self, run):
        """
        The make_results_directory function creates a directory in the output_directory_path for each training run.
        The function saves the model weights and architecture to this directory, as well as a text file containing all
        the parameters used for that particular training run.

        :param run: Pass the run dictionary to the function
        """
        results_directory_path = self.get_file_path([self.output_directory_path, ("training_results_run_" + str(run["RunUID"]))])
        os.mkdir(results_directory_path)
        os.mkdir((results_directory_path + "/ml_model_weights"))
        self.machine_learning.save_model_weights((results_directory_path + "/ml_model_weights"), "ml_model_weights")
        self.machine_learning.save_model(results_directory_path, "ml_model")
        with open(results_directory_path + "/training_run_parameters.txt", "a", newline='') as file:
            file.write("This is a summary of the parameters for this Model:")
            for line in run:
                file.write("\n" + line + ": " + str(run[line]))
