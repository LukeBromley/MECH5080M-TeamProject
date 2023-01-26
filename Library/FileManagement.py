import json
from Library.infrastructure import Node, Path, TrafficLight
from Library.vehicles import Car

"""
Explanation of File Management

Junction Files
    .junc files are identical to .json files but with the name extension changed.
    The .json files are generated from a dictionary containing two entries (nodes and paths).
    Both entries contain 2D lists which contain the information about each node / path

"""


class Configuration:

    def __init__(self, lanes: list,
                 min_start_velocity: float,
                 max_start_velocity: float,
                 min_start_acceleration: float,
                 max_start_acceleration: float,
                 min_length: int,
                 max_length: int,
                 min_width: int,
                 max_width: int,
                 max_num_cars: int
                 ):
        self.lanes = lanes
        self.min_start_velocity = min_start_velocity
        self.max_start_velocity = max_start_velocity
        self.min_start_acceleration = min_start_acceleration
        self.max_start_acceleration = max_start_acceleration
        self.min_length = min_length
        self.max_length = max_length
        self.min_width = min_width
        self.max_width = max_width
        self.max_num_cars = max_num_cars


class FileManagement:
    def __init__(self) -> None:
        """
        Class methods used to:
            save and load .junc files
            save and load simulation results files (TO BE COMPLETED)
        """
        # Configuration identifiers
        self.lanes_key = "lanes"
        self.min_start_velocity_key = "min_start_velocity"
        self.max_start_velocity_key = "max_start_velocity"
        self.min_start_acceleration_key = "min_start_acceleration"
        self.max_start_acceleration_key = "max_start_acceleration"
        self.min_length_key = "min_car_length"
        self.max_length_key = "max_car_length"
        self.min_width_key = "min_car_width"
        self.max_width_key = "max_car_length"
        self.max_num_cars_key = "max_number_of_cars"

        # Junction identifiers
        self.nodes_key = "nodes"
        self.paths_key = "paths"
        self.lights_key = "lights"

        # Car results data identifiers
        self.start_time_key = "start_time"
        self.position_data_key = "position_data"

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
            nodes.append(Node(int(uid), node_data[0], node_data[1], node_data[2]))

        # Load path data
        paths = []
        for uid in file_dict[self.paths_key]:
            path_data = file_dict[self.paths_key][uid]

            start_node = None
            end_node = None
            for node in nodes:
                if node.uid == path_data[0]:
                    start_node = node
                if node.uid == path_data[1]:
                    end_node = node
            if quick_load:
                paths.append(Path(int(uid), start_node, end_node, discrete_length_increment_size=0.1, discrete_iteration_qty=1000))
            else:
                paths.append(Path(int(uid), start_node, end_node))

        # Load light data
        lights = []
        for uid in file_dict[self.lights_key]:
            path_list = []
            for path_uid in file_dict[self.lights_key][uid][0]:
                for path in paths:
                    if path.uid == int(path_uid):
                        path_list.append(path)
            lights.append(TrafficLight(int(uid), path_list))

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
        file_dict = {self.nodes_key: {}, self.paths_key: {}, self.lights_key: {}}

        # Add node data
        for node in nodes:
            file_dict[self.nodes_key][str(node.uid)] = [node.x, node.y, node.angle]

        # Add path data
        for path in paths:
            file_dict[self.paths_key][str(path.uid)] = [path.start_node.uid,
                                                        path.end_node.uid]

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

        file_dict[self.lanes_key] = config.lanes
        file_dict[self.min_start_velocity_key] = config.min_start_velocity
        file_dict[self.max_start_velocity_key] = config.max_start_velocity
        file_dict[self.min_start_acceleration_key] = config.min_start_acceleration
        file_dict[self.max_start_acceleration_key] = config.max_start_acceleration
        file_dict[self.min_length_key] = config.min_length
        file_dict[self.max_length_key] = config.max_length
        file_dict[self.min_width_key] = config.min_width
        file_dict[self.max_width_key] = config.max_width
        file_dict[self.max_num_cars_key] = config.max_num_cars

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def load_config_file(self, file_path: str) -> Configuration:
        """

        :param file_path: where to load configuration from
        :return: the loaded configuration
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        lanes = file_dict[self.lanes_key]
        min_start_velocity = file_dict[self.min_start_velocity_key]
        max_start_velocity = file_dict[self.max_start_velocity_key]
        min_start_acceleration = file_dict[self.min_start_acceleration_key]
        max_start_acceleration = file_dict[self.max_start_acceleration_key]
        min_length = file_dict[self.min_length_key]
        max_length = file_dict[self.max_length_key]
        min_width = file_dict[self.min_width_key]
        max_width = file_dict[self.max_width_key]
        max_num_cars = file_dict[self.max_num_cars_key]

        configuration = Configuration(lanes, min_start_velocity, max_start_velocity, min_start_acceleration,
                                      max_start_acceleration, min_length, max_length, min_width, max_width,
                                      max_num_cars)

        return configuration

    def save_results_data_file(self, file_path: str, cars: list) -> None:
        """

        saving car position data to a file
        :param file_path: where the results data file is saved
        :param cars: list of car objects
        :return: None
        """
        file_dict = {}

        for car in cars:
            file_dict[str(car.uid)] = {}
            file_dict[str(car.uid)][self.start_time_key] = car.start_time
            file_dict[str(car.uid)][self.position_data_key] = car.position_data

        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def load_results_data_file(self, file_path: str) -> list:
        """

        :param file_path: where to load the results data from
        :return: the car results data
        """
        with open(file_path, "r") as file:
            file_dict = json.load(file)

            cars = []
            for uid in file_dict:
                start_time = file_dict[uid][self.start_time_key]
                position_data = file_dict[uid][self.position_data_key]
                cars.append(str(uid), start_time, position_data)

            return cars

