import json
from Library.infrastructure import Node
from Library.infrastructure import Path


class JunctionFileManagement:
    def __init__(self):
        pass

    def load_from_file(self, file_path):
        with open(file_path, "r") as file:
            file_dict = json.load(file)

        nodes = []
        for uid in file_dict["nodes"]:
            node_data = file_dict["nodes"][uid]
            nodes.append(Node(int(uid), node_data[0], node_data[1], node_data[2]))

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

        return nodes, paths

    def save_to_file(self, file_path, nodes, paths):
        file_dict = {"nodes": {}, "paths": {}}

        for node in nodes:
            file_dict["nodes"][str(node.uid)] = [node.x, node.y, node.angle]

        for path in paths:
            file_dict["paths"][str(path.uid)] = [path.start_node.uid,
                                                 path.end_node.uid,
                                                 path.poly_order
                                                 ]

        with open(file_path, "w") as file:
            json.dump(file_dict, file)








