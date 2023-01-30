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
        self.lights = []
        self.vehicles = []
        self._route_designs = []
        self.routes = []
        self.vehicle_results = []

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(
            junction_file_location, quick_load=quick_load)
        for path in self.paths:
            path.calculate_all(self)

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(
            junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_config_file(config_file_location)

    def generate_routes(self):
        nodes_uid = self.get_uid_list(self.nodes)
        start_nodes = nodes_uid.copy()
        end_nodes = nodes_uid.copy()
        for path in self.paths:
            if path.end_node in start_nodes:
                start_nodes.remove(path.end_node)
            if path.start_node in end_nodes:
                end_nodes.remove(path.start_node)
        self.find_routes(start_nodes, end_nodes)
        self.build_routes()

    def find_routes(self, start_nodes, end_nodes): 
        potential_routes = []
        for node in start_nodes:
            paths = self.get_paths_from_start_node(node)
            for path in paths:
                potential_routes.append([path])
        while len(potential_routes):
            to_remove = []
            for route in potential_routes:
                current_route = route.copy()
                new_start_node = (self.get_path(route[-1])).end_node
                following_paths = self.get_paths_from_start_node(new_start_node)
                for k, path in enumerate(following_paths):
                    if path not in route:
                        if k == 0:
                            route.append(path)
                        else:
                            new_route = current_route.copy()
                            new_route.append(path)
                            potential_routes.append(new_route)
                    elif k == 0:
                        to_remove.append(route)  
            for route in potential_routes:
                if (self.get_path(route[-1])).end_node in end_nodes:
                    shorter_path = False
                    for existing_route in self._route_designs:
                        if (self.get_path(existing_route[0]).start_node) == (self.get_path(route[0]).start_node) and (self.get_path(existing_route[-1]).end_node) == (self.get_path(route[-1]).end_node):
                            shorter_path = True
                    if shorter_path == False:
                        self._route_designs.append(route)
                    to_remove.append(route)
            for route in to_remove:
                potential_routes.remove(route)

    def build_routes(self):
        for index, route in enumerate(self._route_designs):
            route_objects = []
            for path in route:
                route_objects.append(self.get_path(path))
            self.routes.append(Route(index, route_objects))

    def get_route_uids(self):
        return list(range(len(self.routes)))

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

    def get_paths_from_start_node(self, node_uid):
        paths = []
        for path in self.paths:
            if path.start_node == node_uid:
                paths.append(path.uid)
        return paths

    def get_light(self, light_uid) -> TrafficLight:
        for light in self.lights:
            if light.uid == light_uid:
                return light

    def get_uid_list(self, object_list=None):
        if object_list is None:
            object_list = []

        uid_list = []
        for object in object_list:
            uid_list.append(object.uid)
        return uid_list

    def get_route(self, route_uid) -> Route:
        for route in self.routes:
            if route.uid == route_uid:
                return route

    def get_vehicles(self) -> List[Vehicle]:
        self.vehicles = [vehicle for vehicle in self.vehicles if vehicle.get_route_distance_travelled() < self.get_route(vehicle.route_uid).length]
        return self.vehicles

    def get_lights(self) -> List[TrafficLight]:
        return self.lights

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
