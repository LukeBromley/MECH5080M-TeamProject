from .FileManagement import FileManagement


class Model:
    def __init__(self, junction_file_location, config_file_location):
        self.file_manager = FileManagement()
        # self.config = self.file_manager.load_config_file(config_file_location)
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location)
        self.cars = []

    def get_node(self, node_uid):
        for node in self.nodes:
            if node.uid == node_uid:
                return node

    def get_path(self, path_uid):
        for path in self.paths:
            if path.uid == path_uid:
                return path

    def get_light(self, light_uid):
        for light in self.lights:
            if light.uid == light_uid:
                return light

