
from typing import List
from random import choice
from .FileManagement import FileManagement
import time
from .infrastructure import Route

class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None
        self.nodes = []
        self.paths = []
        self.lights = []
        self.vehicles = []
        self._routes = []

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(
            junction_file_location, quick_load=quick_load)
        for path in self.paths:
            path.calculate_all(self)
        # self.lights.calculate_all()

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
        #connected_nodes = [[] for node in nodes_uid]
        #for path in self.paths:
            #node_index = nodes_uid.index(path.start_node)
            #connected_nodes[node_index].append(path.end_node)
        self.find_routes(start_nodes, end_nodes) # nodes_uid, connected_nodes)

    def find_routes(self, start_nodes, end_nodes): #nodes_uid, connected_nodes):
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
                    self._routes.append(route)
                    to_remove.append(route)
            for route in to_remove:
                potential_routes.remove(route)
        print(self._routes)

    def get_route(self):
        route = choice(self._routes)
        route_objects = []
        for path in route:
            route_objects.append(self.get_path(path))
        print(route_objects)
        return Route(route_objects)

    def get_node(self, node_uid):
        for node in self.nodes:
            if node.uid == node_uid:
                return node

    def get_path(self, path_uid):
        for path in self.paths:
            if path.uid == path_uid:
                return path

    def get_paths_from_start_node(self, node_uid):
        paths = []
        for path in self.paths:
            if path.start_node == node_uid:
                paths.append(path.uid)
        return paths

    def get_light(self, light_uid):
        for light in self.lights:
            if light.uid == light_uid:
                return light

    def get_vehicle(self, vehicle_uid):
        for vehicle in self.vehicles:
            if vehicle.uid == vehicle_uid:
                return vehicle

    def get_uid_list(self, object_list: List = []):
        uid_list = []
        for object in object_list:
            uid_list.append(object.uid)
        return uid_list

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
