import json
import csv
from library.environment import SimulationConfiguration, Time, MachineLearningConfiguration
from library.infrastructure import Node, Path, TrafficLight
from library.vehicles import VehicleResults


"""
Explanation of File Management

Junction Files
    .junc files are identical to .json files but with the name extension changed.
    The .json files are generated from a dictionary containing two entries (nodes and paths).
    Both entries contain 2D lists which contain the information about each node / path

"""


class FileManagement:
    def __init__(self) -> None:
        """
        Class methods used to:
            save and load .junc files
            save and load simulation results files (TO BE COMPLETED)
        """
        # SIMULATION CONFIG
        # General
        self.tick_rate_key = "tick_rate"
        self.start_time_of_day_key = "start_time_of_day"
        self.simulation_duration_key = "simulation_duration"
        # Vehicle
        self.initial_speed_key = "initial_speed"
        self.initial_acceleration_key = "initial_acceleration"
        self.maximum_acceleration_key = "maximum_acceleration"
        self.maximum_deceleration_key = "maximum_deceleration"
        self.preferred_time_gap_key = "preferred_time_gap"
        self.maximum_speed_key = "maximum_speed"
        self.min_creep_distance_key = "min_creep_distance"
        # Spawning
        self.random_seed_key = "random_seed"
        self.max_spawn_time_key = "max_spawn_time"
        self.min_spawn_time_key = "min_spawn_time"
        self.mean_spawn_time_per_hour_key = "mean_spawn_time_per_hour"
        self.sdev_spawn_time_per_hour_key = "sdev_spawn_time_per_hour"
        self.min_spawn_time_per_hour_key = "min_spawn_time_per_hour"
        self.max_car_length_key = "max_car_length"
        self.min_car_length_key = "min_car_length"
        self.max_car_width_key = "max_car_width"
        self.min_car_width_key = "min_car_width"
        self.mean_car_lengths_key = "mean_car_lengths"
        self.mean_car_widths_key = "mean_car_widths"
        self.sdev_car_lengths_key = "sdev_car_lengths"
        self.sdev_car_widths_key = "sdev_car_widths"
        # Visualiser
        self.visualiser_scale_key = "visualiser_scale"
        # Junction identifiers
        self.nodes_key = "nodes"
        self.paths_key = "paths"
        self.lights_key = "lights"

        # RESULTS
        self.start_time_key = "start_time"
        self.position_data_key = "position_data"

        # MACHINE LEARNING CONFIG
        self.config_id_key = "config_id"
        # Limits
        self.max_steps_per_episode_key = "max_steps_per_episode"
        self.episode_end_reward_key = "episode_end_reward"
        self.solved_mean_reward_key = "solved_mean_reward"
        self.reward_history_limit_key = "reward_history_limit"
        # Action Probabilities
        self.random_action_selection_probabilities_key = "random_action_selection_probabilities"
        self.epsilon_greedy_min_key = "epsilon_greedy_min"
        self.epsilon_greedy_max_key = "epsilon_greedy_max"
        # Exploration
        self.number_of_steps_of_required_exploration_key = "number_of_steps_of_required_exploration"
        self.number_of_steps_of_exploration_reduction_key = "number_of_steps_of_exploration_reduction"
        # Update
        self.update_after_actions_key = "update_after_actions"
        self.update_target_network_key = "update_target_network"
        # Look Into Future
        self.seconds_to_look_into_the_future_key = "seconds_to_look_into_the_future"
        # Sample Size
        self.sample_size_key = "sample_size"
        # Discount factor
        self.gamma_key = "gamma"
        # Maximum replay buffer length
        self.max_replay_buffer_length_key = "max_replay_buffer_length"
        # Optimisations
        self.learning_rate_key = "learning_rate"
        self.ml_model_hidden_layers_key = "ml_model_hidden_layers"

    def load_from_junction_file(self, file_path: str, quick_load=False) -> tuple:
        """
        The load_from_junction_file function is used to load a junction (.junc) file into the model. Model components loaded
        include: nodes, paths and lights.
        If quick_load is used then paths will also automatically have their discrete points calculated with low
        accuracy.

        :param file_path: Specify the file path of the junction file to be loaded
        :param quick_load: Speed up path the loading process
        :return: A tuple of nodes, paths and lights
        """

        self.update_junction_file(file_path)

        # Open the file
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        # Load node data
        nodes = []
        for uid in file_dict[self.nodes_key]:
            node_data = file_dict[self.nodes_key][uid]
            nodes.append(
                Node(int(uid), node_data[0], node_data[1], node_data[2]))

        # Load path data
        paths = []
        for uid in file_dict[self.paths_key]:
            path_data = file_dict[self.paths_key][uid]
            if quick_load:
                paths.append(Path(int(uid), path_data[0], path_data[1], discrete_length_increment_size=0.1,
                             discrete_iteration_qty=1000, parallel_paths=path_data[2]))
            else:
                paths.append(
                    Path(int(uid), path_data[0], path_data[1], parallel_paths=path_data[2]))

        # Load light data
        lights = []
        for uid in file_dict[self.lights_key]:
            lights.append(TrafficLight(
                int(uid), file_dict[self.lights_key][uid][0]))

        # Return the data
        return nodes, paths, lights

    def save_to_junction_file(self, file_path: str, nodes: list, paths: list, lights: list) -> None:
        """
        Saves the nodes, paths and lights from the model to a junction (.junc) file.

        :param file_path: file path of where to save .junc file
        :param nodes: list of nodes
        :param paths: list of paths
        :param lights: list of lights
        :return: None
        """
        # Create dictionary structure
        file_dict = {self.nodes_key: {},
                     self.paths_key: {}, self.lights_key: {}}

        # Add node data
        for node in nodes:
            file_dict[self.nodes_key][str(node.uid)] = [
                node.x, node.y, node.angle]

        # Add path data
        for path in paths:
            file_dict[self.paths_key][str(path.uid)] = [path.start_node_uid,
                                                        path.end_node_uid,
                                                        path.parallel_paths]

        # Add light data
        for light in lights:
            file_dict[self.lights_key][str(light.uid)] = [
                [path.uid for path in light.paths]
            ]

        # Save dictionary as .json
        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def update_junction_file(self, file_path: str) -> None:
        """

        Changes any old file that does not contain all dictionary keys and adds the relevant keys. This helps with
        compatability.

        :param file_path: Specify the file path of the junction file to be loaded
        :return: None
        """

        # Open the file
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        if self.nodes_key not in file_dict:
            file_dict[self.nodes_key] = {}

        if self.paths_key not in file_dict:
            file_dict[self.paths_key] = {}

        for path in file_dict[self.paths_key]:
            while len(file_dict[self.paths_key][path]) < 3:
                file_dict[self.paths_key][path].append([])

        if self.lights_key not in file_dict:
            file_dict["lights"] = {}

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def save_sim_config_file(self, file_path: str, s_config: SimulationConfiguration) -> None:
        """

        Saves configuration (.config) file based on the parameters set.

        :param file_path: where the config file is saved
        :param config: configuration to be saved
        :return: None
        """

        # Create dictionary structure
        file_dict = {}

        # Configuration identifiers
        file_dict[self.tick_rate_key] = s_config.tick_rate
        file_dict[self.start_time_of_day_key] = [s_config.start_time_of_day.hour, s_config.start_time_of_day.minute, s_config.start_time_of_day.second]
        file_dict[self.simulation_duration_key] = s_config.simulation_duration

        # Vehicle
        file_dict[self.initial_speed_key] = s_config.initial_speed
        file_dict[self.initial_acceleration_key] = s_config.initial_acceleration
        file_dict[self.maximum_acceleration_key] = s_config.maximum_acceleration
        file_dict[self.maximum_deceleration_key] = s_config.maximum_deceleration
        file_dict[self.preferred_time_gap_key] = s_config.preferred_time_gap
        file_dict[self.maximum_speed_key] = s_config.maximum_speed
        file_dict[self.min_creep_distance_key] = s_config.min_creep_distance

        # Spawning
        file_dict[self.random_seed_key] = s_config.random_seed

        file_dict[self.max_spawn_time_key] = s_config.max_spawn_time
        file_dict[self.min_spawn_time_key] = s_config.min_spawn_time
        file_dict[self.mean_spawn_time_per_hour_key] = s_config.mean_spawn_time_per_hour
        file_dict[self.sdev_spawn_time_per_hour_key] = s_config.sdev_spawn_time_per_hour
        file_dict[self.min_spawn_time_per_hour_key] = s_config.min_spawn_time_per_hour

        file_dict[self.max_car_length_key] = s_config.max_vehicle_length
        file_dict[self.min_car_length_key] = s_config.min_vehicle_length
        file_dict[self.max_car_width_key] = s_config.max_vehicle_width
        file_dict[self.min_car_width_key] = s_config.min_vehicle_width

        file_dict[self.mean_car_lengths_key] = s_config.mean_vehicle_lengths
        file_dict[self.mean_car_widths_key] = s_config.mean_vehicle_widths
        file_dict[self.sdev_car_lengths_key] = s_config.sdev_vehicle_lengths
        file_dict[self.sdev_car_widths_key] = s_config.sdev_vehicle_widths

        # Visualiser
        file_dict[self.visualiser_scale_key] = s_config.visualiser_scale

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def load_sim_config_file(self, file_path: str) -> SimulationConfiguration:
        """

        Loads configuration (.config) file based from specified file path.

        :param file_path: file path of configuration file
        :return: the loaded configuration
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        s_config = SimulationConfiguration()

        # Configuration identifiers
        s_config.tick_rate = file_dict[self.tick_rate_key]
        s_config.start_time_of_day = Time(file_dict[self.start_time_of_day_key][0], file_dict[self.start_time_of_day_key][1], file_dict[self.start_time_of_day_key][2])
        s_config.simulation_duration = file_dict[self.simulation_duration_key]

        # Vehicle
        s_config.initial_speed = file_dict[self.initial_speed_key]
        s_config.initial_acceleration = file_dict[self.initial_acceleration_key]
        s_config.maximum_acceleration = file_dict[self.maximum_acceleration_key]
        s_config.maximum_deceleration = file_dict[self.maximum_deceleration_key]
        s_config.preferred_time_gap = file_dict[self.preferred_time_gap_key]
        s_config.maximum_speed = file_dict[self.maximum_speed_key]
        s_config.min_creep_distance = file_dict[self.min_creep_distance_key]

        # Spawning
        s_config.random_seed = file_dict[self.random_seed_key]

        s_config.max_spawn_time = file_dict[self.max_spawn_time_key]
        s_config.min_spawn_time = file_dict[self.min_spawn_time_key]
        s_config.mean_spawn_time_per_hour = file_dict[self.mean_spawn_time_per_hour_key]
        s_config.sdev_spawn_time_per_hour = file_dict[self.sdev_spawn_time_per_hour_key]
        s_config.min_spawn_time_per_hour = file_dict[self.min_spawn_time_per_hour_key]

        s_config.max_car_length = file_dict[self.max_car_length_key]
        s_config.min_car_length = file_dict[self.min_car_length_key]
        s_config.max_car_width = file_dict[self.max_car_width_key]
        s_config.min_car_width = file_dict[self.min_car_width_key]

        s_config.mean_car_lengths = file_dict[self.mean_car_lengths_key]
        s_config.mean_car_widths = file_dict[self.mean_car_widths_key]
        s_config.sdev_car_lengths = file_dict[self.sdev_car_lengths_key]
        s_config.sdev_car_widths = file_dict[self.sdev_car_widths_key]

        # Visualiser
        s_config.visualiser_scale = file_dict[self.visualiser_scale_key]

        return s_config

    def save_results_data_file(self, file_path: str, vehicles: list) -> None:
        """

        Saves vehicle positions over time to results file.

        :param file_path: where the results data file is saved
        :param vehicles: list of vehicle objects
        :return: None
        """
        file_dict = {}

        for vehicle in vehicles:
            file_dict[str(vehicle.uid)] = {}
            file_dict[str(vehicle.uid)
                      ][self.start_time_key] = vehicle.start_time
            file_dict[str(vehicle.uid)
                      ][self.position_data_key] = vehicle.position_data

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def load_results_data_file(self, file_path: str) -> list:
        """

        Loads vehicle positions over time from results file.

        :param file_path: where to load the results data from
        :return: list of the vehicle results
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)

            vehicles = []
            for uid in file_dict:
                start_time = file_dict[uid][self.start_time_key]
                position_data = file_dict[uid][self.position_data_key]
                vehicles.append(VehicleResults(
                    int(uid), start_time, position_data))

            return vehicles

    def load_ml_configs_from_file(self, file_path: str) -> list:
        """
        Takes a file path as an argument and returns a list of machine learning configs.
        The function opens the file at the given path, reads each line in the file, and converts each line into a
        dictionary which is then read and converted to a MachineLearningConfiguration class object.

        :param file_path: str: Specify the path to the file that contains
        :return: A list of MachineLearningConfiguration objects
        """
        machine_learning_configs = []
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            for file_dict in csv_reader:
                machine_learning_configs.append(self.load_ml_config(file_dict))
        return machine_learning_configs

    def load_ml_config(self, file_dict: dict) -> MachineLearningConfiguration:
        """
        The load_ml_config function takes a dictionary of key-value pairs and returns an instance of the
        MachineLearningConfiguration class that stores the values.

        :param file_dict: Configuration dictionary
        :return: A MachineLearningConfiguration object
        """

        ml_config = MachineLearningConfiguration()
        # Config
        ml_config.config_id = self.try_get(file_dict, self.config_id_key)

        # Limits
        ml_config.max_steps_per_episode = self.try_get(file_dict, self.max_steps_per_episode_key)
        ml_config.episode_end_reward = self.try_get(file_dict, self.episode_end_reward_key)
        ml_config.solved_mean_reward = self.try_get(file_dict, self.solved_mean_reward_key)
        ml_config.reward_history_limit = self.try_get(file_dict, self.reward_history_limit_key)

        # Action Probabilities
        ml_config.random_action_selection_probabilities = self.try_get(file_dict, self.random_action_selection_probabilities_key)
        ml_config.epsilon_greedy_min = self.try_get(file_dict, self.epsilon_greedy_min_key)
        ml_config.epsilon_greedy_max = self.try_get(file_dict, self.epsilon_greedy_max_key)

        # Exploration
        ml_config.number_of_steps_of_required_exploration = self.try_get(file_dict, self.number_of_steps_of_required_exploration_key)
        ml_config.number_of_steps_of_exploration_reduction = self.try_get(file_dict, self.number_of_steps_of_exploration_reduction_key)

        # Update
        ml_config.update_after_actions = self.try_get(file_dict, self.update_after_actions_key)
        ml_config.update_target_network = self.try_get(file_dict, self.update_target_network_key)

        # Look Into Future
        ml_config.seconds_to_look_into_the_future = self.try_get(file_dict, self.seconds_to_look_into_the_future_key)

        # Sample Size
        ml_config.sample_size = self.try_get(file_dict, self.sample_size_key)

        # Discount factor
        ml_config.gamma = self.try_get(file_dict, self.gamma_key)

        # Maximum replay buffer length
        ml_config.max_replay_buffer_length = self.try_get(file_dict, self.max_replay_buffer_length_key)

        # Optimisations
        ml_config.learning_rate = self.try_get(file_dict, self.learning_rate_key)
        ml_config.ml_model_hidden_layers = self.try_get(file_dict, self.ml_model_hidden_layers_key)

        return ml_config

    def try_get(self, file_dict, string):
        """
        The try_get function is used to try and get a value from the file_dict.
        If it fails, it returns None. If it succeeds, then we check if the value is an int or float
        and convert accordingly.

        :param file_dict: Store the data from the file
        :param string: Get the value from the dictionary
        :return: The value of the key in the dictionary
        """
        try:
            value = file_dict[string]
            try:
                if "|" in value:
                    value = list(map(int, value.split("|")))
                else:
                    value = int(value)
            except ValueError:
                if "|" in value:
                    value = list(map(float, value.split("|")))
                else:
                    value = float(value)
        except KeyError:
            value = None
        return value
