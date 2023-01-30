from .FileManagement import FileManagement
from Library.infrastructure import Node, Path, TrafficLight


class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None
        self.nodes = []
        self.paths = []
        self.lights = []
        self.vehicles = []
        self.vehicle_results = []

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location, quick_load=quick_load)
        for path in self.paths:
            path.calculate_all(self)
        # self.lights.calculate_all()

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_config_file(config_file_location)

    def save_results(self, results_file_location):
        self.file_manager.save_results_data_file(results_file_location, self.vehicles)

    def load_results(self, results_file_location):
        self.vehicle_results = self.file_manager.load_results_data_file(results_file_location)

    # NODES

    def get_node(self, node_uid):
        for node in self.nodes:
            if node.uid == node_uid:
                return node

    def get_node_index(self, node_uid):
        for index, node in enumerate(self.nodes):
            if node.uid == node_uid:
                return index

    def set_node(self, node):
        index = self.get_node_index(node.uid)
        self.nodes[index] = node

    def update_node(self, node_uid, x=None, y=None, a=None):
        index = self.get_node_index(node_uid)
        if x is not None:
            self.nodes[index].x = x
        if y is not None:
            self.nodes[index].y = y
        if a is not None:
            self.nodes[index].a = a

    def add_node(self, x, y, a):
        node_uid = 1
        if len(self.nodes) > 0:
            node_uid = max([node.uid for node in self.nodes]) + 1
        self.nodes.append(Node(node_uid, x, y, a))

    def remove_node(self, node_uid):
        path_uids_to_remove = []
        for path in self.paths:
            if path.start_node == node_uid or path.end_node == node_uid:
                path_uids_to_remove.append(path.uid)

        for path_uid in path_uids_to_remove:
            self.remove_path(path_uid)

        index = self.get_node_index(node_uid)
        self.nodes.pop(index)

    # PATHS

    def get_path(self, path_uid):
        for path in self.paths:
            if path.uid == path_uid:
                return path

    def get_path_index(self, path_uid):
        for index, path in enumerate(self.paths):
            if path.uid == path_uid:
                return index

    def set_path(self, path):
        index = self.get_path_index(path.uid)
        self.paths[index] = path

    def update_path(self, path_uid, start_node_uid=None, end_node_uid=None):
        index = self.get_path_index(path_uid)
        if start_node_uid is not None:
            self.paths[index].start_node = start_node_uid
        if end_node_uid is not None:
            self.paths[index].end_node = end_node_uid

    def add_path(self, start_node_uid, end_node_uid):
        path_uid = 1
        if len(self.paths) > 0:
            path_uid = max([path.uid for path in self.paths]) + 1
        self.paths.append(Path(path_uid, start_node_uid, end_node_uid))

    def remove_path(self, path_uid):
        index = self.get_path_index(path_uid)
        self.paths.pop(index)

    # LIGHTS

    def get_light(self, light_uid):
        for light in self.lights:
            if light.uid == light_uid:
                return light

    def get_light_index(self, light_uid):
        for index, light in enumerate(self.lightw):
            if light.uid == light_uid:
                return index

    def set_light(self, light):
        index = self.get_path_index(light.uid)
        self.lights[index] = light

    def add_light(self):
        light_uid = 1
        if len(self.paths) > 0:
            light_uid = max([light.uid for light in self.lights]) + 1
        self.lights.append(TrafficLight(light_uid))

    def remove_light(self, light_uid):
        index = self.get_light_index(light_uid)
        self.lights.pop(index)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

