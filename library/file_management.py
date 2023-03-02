import json
import csv
from library.environment import Configuration, Time, MLConfiguration
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
        # Configuration identifiers
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

        # Car results data identifiers
        self.start_time_key = "start_time"
        self.position_data_key = "position_data"

        # MACHINE LEARNING
        # Config
        self.config_id_key = "config_id"
        # Limits
        self.max_steps_per_episode_key = "max_steps_per_episode"
        self.episode_end_reward_key = "episode_end_reward"
        self.solved_mean_reward_key = "solved_mean_reward"

        # Action Probabilities
        self.random_action_do_nothing_probability_key = "random_action_do_nothing_probability"
        self.epsilon_greedy_min_key = "epsilon_greedy_min"
        self.epsilon_greedy_max_key = "epsilon_greedy_max"

        # Exploration
        self.number_of_steps_of_required_exploration_key = "number_of_steps_of_required_exploration"
        self.number_of_steps_of_exploration_reduction_key = "number_of_steps_of_exploration_reduction"

        # Sample Size
        self.sample_size_key = "sample_size"

        # Discount factor
        self.gamma_key = "gamma"

        # Maximum replay buffer length
        self.max_replay_buffer_length_key = "max_replay_buffer_length"

        # Optimisations
        self.learning_rate_key = "learning_rate"

        # Train the model after number of actions
        self.update_after_actions_key = "update_after_actions"

        # How often to update the target network
        self.update_target_network_key = "update_target_network"

        self.header = [self.config_id_key, self.max_steps_per_episode_key, self.episode_end_reward_key, self.solved_mean_reward_key,
                       self.random_action_do_nothing_probability_key, self.epsilon_greedy_min_key,
                       self.epsilon_greedy_max_key, self.number_of_steps_of_required_exploration_key,
                       self.number_of_steps_of_exploration_reduction_key, self.sample_size_key, self.gamma_key,
                       self.max_replay_buffer_length_key, self.learning_rate_key, self.update_after_actions_key,
                       self.update_target_network_key]


    def load_from_junction_file(self, file_path: str, quick_load=False) -> tuple:
        """

        :param file_path: file path of .junc file
        :return: nodes, paths: data contained in .junc file
        """

        # Update File To Latest Version
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

    def save_to_junction_file(self, file_path, nodes: list, paths: list, lights: list) -> None:
        """

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

        :param file_path: Changes any old file that does not contain all dictionary keys and adds the relevant keys
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

    def save_config_file(self, file_path: str, config: Configuration) -> None:
        """

        :param file_path: where the config file is saved
        :param config: configuration to be saved
        :return: None
        """

        # Create dictionary structure
        file_dict = {}

        # Configuration identifiers
        file_dict[self.tick_rate_key] = config.tick_rate
        file_dict[self.start_time_of_day_key] = [config.start_time_of_day.hour, config.start_time_of_day.minute, config.start_time_of_day.second]
        file_dict[self.simulation_duration_key] = config.simulation_duration

        # Vehicle
        file_dict[self.initial_speed_key] = config.initial_speed
        file_dict[self.initial_acceleration_key] = config.initial_acceleration
        file_dict[self.maximum_acceleration_key] = config.maximum_acceleration
        file_dict[self.maximum_deceleration_key] = config.maximum_deceleration
        file_dict[self.preferred_time_gap_key] = config.preferred_time_gap
        file_dict[self.maximum_speed_key] = config.maximum_speed
        file_dict[self.min_creep_distance_key] = config.min_creep_distance

        # Spawning
        file_dict[self.random_seed_key] = config.random_seed

        file_dict[self.max_spawn_time_key] = config.max_spawn_time
        file_dict[self.min_spawn_time_key] = config.min_spawn_time
        file_dict[self.mean_spawn_time_per_hour_key] = config.mean_spawn_time_per_hour
        file_dict[self.sdev_spawn_time_per_hour_key] = config.sdev_spawn_time_per_hour

        file_dict[self.max_car_length_key] = config.max_car_length
        file_dict[self.min_car_length_key] = config.min_car_length
        file_dict[self.max_car_width_key] = config.max_car_width
        file_dict[self.min_car_width_key] = config.min_car_width

        file_dict[self.mean_car_lengths_key] = config.mean_car_lengths
        file_dict[self.mean_car_widths_key] = config.mean_car_widths
        file_dict[self.sdev_car_lengths_key] = config.sdev_car_lengths
        file_dict[self.sdev_car_widths_key] = config.sdev_car_widths

        # Visualiser
        file_dict[self.visualiser_scale_key] = config.visualiser_scale

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def load_config_file(self, file_path: str) -> Configuration:
        """

        :param file_path: where to load configuration from
        :return: the loaded configuration
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        config = Configuration()

        # Configuration identifiers
        config.tick_rate = file_dict[self.tick_rate_key]
        config.start_time_of_day = Time(file_dict[self.start_time_of_day_key][0], file_dict[self.start_time_of_day_key][1], file_dict[self.start_time_of_day_key][2])
        config.simulation_duration = file_dict[self.simulation_duration_key]

        # Vehicle
        config.initial_speed = file_dict[self.initial_speed_key]
        config.initial_acceleration = file_dict[self.initial_acceleration_key]
        config.maximum_acceleration = file_dict[self.maximum_acceleration_key]
        config.maximum_deceleration = file_dict[self.maximum_deceleration_key]
        config.preferred_time_gap = file_dict[self.preferred_time_gap_key]
        config.maximum_speed = file_dict[self.maximum_speed_key]
        config.min_creep_distance = file_dict[self.min_creep_distance_key]

        # Spawning
        config.random_seed = file_dict[self.random_seed_key]

        config.max_spawn_time = file_dict[self.max_spawn_time_key]
        config.min_spawn_time = file_dict[self.min_spawn_time_key]
        config.mean_spawn_time_per_hour = file_dict[self.mean_spawn_time_per_hour_key]
        config.sdev_spawn_time_per_hour = file_dict[self.sdev_spawn_time_per_hour_key]

        config.max_car_length = file_dict[self.max_car_length_key]
        config.min_car_length = file_dict[self.min_car_length_key]
        config.max_car_width = file_dict[self.max_car_width_key]
        config.min_car_width = file_dict[self.min_car_width_key]

        config.mean_car_lengths = file_dict[self.mean_car_lengths_key]
        config.mean_car_widths = file_dict[self.mean_car_widths_key]
        config.sdev_car_lengths = file_dict[self.sdev_car_lengths_key]
        config.sdev_car_widths = file_dict[self.sdev_car_widths_key]

        # Visualiser
        config.visualiser_scale = file_dict[self.visualiser_scale_key]

        return config

    def save_results_data_file(self, file_path: str, vehicles: list) -> None:
        """

        saving car position data to a file
        :param file_path: where the results data file is saved
        :param cars: list of car objects
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

        :param file_path: where to load the results data from
        :return: the car results data
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
        
    def save_ML_configs_to_file(self, file_path, ml_configs):
        with open(file_path, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.header)
            writer.writeheader()
            for i, config in enumerate(ml_configs):
                file_dict = self.save_ML_config(config, i)
                writer.writerow(file_dict)

    def save_ML_config(self, config, i) -> None:
        """

        :param file_path: where the ML config file is saved
        :param config: ML configuration to be saved
        :return: None
        """

        # Create dictionary structure
        file_dict = {}
        # Config
        file_dict[self.config_id_key] = i

        # Limits
        file_dict[self.max_steps_per_episode_key] = config.max_steps_per_episode
        file_dict[self.episode_end_reward_key] = config.episode_end_reward
        file_dict[self.solved_mean_reward_key] = config.solved_mean_reward

        # Action Probabilities
        file_dict[self.random_action_do_nothing_probability_key] = config.random_action_do_nothing_probability
        file_dict[self.epsilon_greedy_min_key] = config.epsilon_greedy_min
        file_dict[self.epsilon_greedy_max_key] = config.epsilon_greedy_max

        # Exploration
        file_dict[self.number_of_steps_of_required_exploration_key] = config.number_of_steps_of_required_exploration
        file_dict[self.number_of_steps_of_exploration_reduction_key] = config.number_of_steps_of_exploration_reduction

        # Sample Size
        file_dict[self.sample_size_key] = config.sample_size

        # Discount factor
        file_dict[self.gamma_key] = config.gamma

        # Maximum replay buffer length
        file_dict[self.max_replay_buffer_length_key] = config.max_replay_buffer_length

        # Optimisations
        file_dict[self.learning_rate_key] = config.learning_rate

        # Train the model after number of actions
        file_dict[self.update_after_actions_key] = config.update_after_actions

        # How often to update the target network
        file_dict[self.update_target_network_key] = config.update_target_network

        return file_dict

    def load_ML_configs_from_file(self, file_path):
        machine_learning_configs = []
        with open(file_path, "r") as file:
            csv_reader = csv.DictReader(file)
            for file_dict in csv_reader:
                machine_learning_configs.append(self.load_ML_config(file_dict))
        return machine_learning_configs

    def load_ML_config(self, file_dict) -> MLConfiguration:
        """

        :param file_path: where to load configuration from
        :return: the loaded configuration
        """
        config = MLConfiguration()

        # Config
        config.config_id = file_dict[self.config_id_key]

        # Limits
        config.max_steps_per_episode = file_dict[self.max_steps_per_episode_key]
        config.episode_end_reward = file_dict[self.episode_end_reward_key]
        config.solved_mean_reward = file_dict[self.solved_mean_reward_key]

        # Action Probabilities
        config.random_action_do_nothing_probability = file_dict[self.random_action_do_nothing_probability_key]
        config.epsilon_greedy_min = file_dict[self.epsilon_greedy_min_key]
        config.epsilon_greedy_max = file_dict[self.epsilon_greedy_max_key]

        # Exploration
        config.number_of_steps_of_required_exploration = file_dict[self.number_of_steps_of_required_exploration_key]
        config.number_of_steps_of_exploration_reduction = file_dict[self.number_of_steps_of_exploration_reduction_key]

        # Sample Size
        config.sample_size = file_dict[self.sample_size_key]

        # Discount factor
        config.gamma = file_dict[self.gamma_key]

        # Maximum replay buffer length
        config.max_replay_buffer_length = file_dict[self.max_replay_buffer_length_key]

        # Optimisations
        config.learning_rate = file_dict[self.learning_rate_key]

        # Train the model after number of actions
        config.update_after_actions = file_dict[self.update_after_actions_key]

        # How often to update the target network
        config.update_target_network = file_dict[self.update_target_network_key]

        return config