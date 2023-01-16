import json
from Library.infrastructure import Node, Path, TrafficLight

"""
Explanation of File Management

Junction Files
    .junc files are identical to .json files but with the name extension changed.
    The .json files are generated from a dictionary containing two entries (nodes and paths).
    Both entries contain 2D lists which contain the information about each node / path

"""


class JunctionFileManagement:
    def __init__(self) -> None:
        """
        Class methods used to:
            save and load .junc files
            save and load simulation results files (TO BE COMPLETED)
        """
        pass

    def load_from_file(self, file_path: str) -> tuple:
        """

        :param file_path: file path of .junc file
        :return: nodes, paths: data contained in .junc file
        """

        # Update File To Latest Version
        self.update_file(file_path)

        # Open the file
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        # Load node data
        nodes = []
        for uid in file_dict["nodes"]:
            node_data = file_dict["nodes"][uid]
            nodes.append(Node(int(uid), node_data[0], node_data[1], node_data[2]))

        # Load path data
        paths = []
        for uid in file_dict["paths"]:
            path_data = file_dict["paths"][uid]

            start_node = None
            end_node = None
            for node in nodes:
                if node.uid == path_data[0]:
                    start_node = node
                if node.uid == path_data[1]:
                    end_node = node

            paths.append(Path(int(uid), start_node, end_node, path_data[2]))

        # Load light data
        lights = []
        for uid in file_dict["lights"]:
            path_list = []
            for path_uid in file_dict["lights"][uid][0]:
                for path in paths:
                    if path.uid == int(path_uid):
                        path_list.append(path)
            lights.append(TrafficLight(int(uid), path_list))

        # Return the data
        return nodes, paths, lights

    def save_to_file(self, file_path, nodes: list, paths: list, lights: list) -> None:
        """

        :param file_path: file path of where to save .junc file
        :param nodes: list of nodes
        :param paths: list of paths
        :param lights: list of lights
        :return: None
        """
        # Create dictionary structure
        file_dict = {"nodes": {}, "paths": {}, "lights": {}}

        # Add node data
        for node in nodes:
            file_dict["nodes"][str(node.uid)] = [node.x, node.y, node.angle]

        # Add path data
        for path in paths:
            file_dict["paths"][str(path.uid)] = [path.start_node.uid,
                                                 path.end_node.uid,
                                                 path.poly_order
                                                 ]

        # Add light data
        for light in lights:
            file_dict["lights"][str(light.uid)] = [
                [path.uid for path in light.paths]
            ]

        # Save dictionary as .json
        with open(file_path, "w") as file:
            json.dump(file_dict, file)

    def update_file(self, file_path: str) -> None:
        """

        :param file_path: Changes any old file that does not contain all dictionary keys and adds the relevant keys
        :return: None
        """

        # Open the file
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        if "nodes" not in file_dict:
            file_dict["nodes"] = {}

        if "paths" not in file_dict:
            file_dict["paths"] = {}

        if "lights" not in file_dict:
            file_dict["lights"] = {}

        with open(file_path, "w") as file:
            json.dump(file_dict, file)










