from .FileManagement import FileManagement


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

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

