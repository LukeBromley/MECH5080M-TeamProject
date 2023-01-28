from typing import List

from .FileManagement import FileManagement
from .infrastructure import Route, Node, Path, TrafficLight
from .vehicles import Vehicle


class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None
        self.nodes = []
        self.paths = []
        self.routes = []
        self.lights = []
        self.vehicles = []
        self.vehicle_results = []

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location, quick_load=quick_load)
        for path in self.paths:
            path.calculate_all(self)

        # TODO: Move to the FileManager.load_from_junction file using graph theory
        self.routes = [
            Route(1, [self.get_path(1), self.get_path(2), self.get_path(3)]),
            Route(2, [self.get_path(4), self.get_path(5), self.get_path(6)])
        ]

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_config_file(config_file_location)

    def save_results(self, results_file_location):
        self.file_manager.save_results_data_file(results_file_location, self.vehicles)

    def load_results(self, results_file_location):
        self.vehicle_results = self.file_manager.load_results_data_file(results_file_location)

    def get_vehicle(self, vehicle_uid) -> Vehicle:
        for vehicle in self.vehicles:
            if vehicle.uid == vehicle_uid:
                return vehicle

    def get_node(self, node_uid) -> Node:
        for node in self.nodes:
            if node.uid == node_uid:
                return node

    def get_path(self, path_uid) -> Path:
        for path in self.paths:
            if path.uid == path_uid:
                return path

    def get_light(self, light_uid) -> TrafficLight:
        for light in self.lights:
            if light.uid == light_uid:
                return light

    def get_route(self, route_uid) -> Route:
        for route in self.routes:
            if route.uid == route_uid:
                return route

    def get_vehicles(self) -> List[Vehicle]:
        self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.get_route_distance_travelled() < self.get_route(vehicle.route_uid).length]
        return self.vehicles

    def get_lights(self):
        return self.lights

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

