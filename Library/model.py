from .FileManagement import FileManagement


class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None
        self.nodes = []
        self.paths = []
        self.lights = []
        self.vehicles = []

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location, quick_load=quick_load)
        for path in self.paths:
            path.calculate_all(self)
        # self.lights.calculate_all()

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_config_file(config_file_location)

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

    def get_vehicles(self):
        self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.get_position() is not None]
        return self.vehicles

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def remove_vehicle(self, index):
        del self.vehicles[index]


