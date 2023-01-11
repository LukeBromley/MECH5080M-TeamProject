import json
from Library.infrastructure import Node
from Library.infrastructure import Path

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

        # Return the data
        return nodes, paths

    def save_to_file(self, file_path, nodes, paths) -> None:
        """

        :param file_path: file path of where to save .junc file
        :param nodes: list of nodes
        :param paths: list of paths
        :return: None
        """
        # Create dictionary structure
        file_dict = {"nodes": {}, "paths": {}}

        # Add node data
        for node in nodes:
            file_dict["nodes"][str(node.uid)] = [node.x, node.y, node.angle]

        # Add path data
        for path in paths:
            file_dict["paths"][str(path.uid)] = [path.start_node.uid,
                                                 path.end_node.uid,
                                                 path.poly_order
                                                 ]

        # Save dictionary as .json
        with open(file_path, "w") as file:
            json.dump(file_dict, file)








