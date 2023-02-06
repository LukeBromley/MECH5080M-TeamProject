from typing import List
from math import floor
from .FileManagement import FileManagement
from Library.infrastructure import Node, Path, TrafficLight, Route
from Library.vehicles import Vehicle


class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None

        self.nodes = []
        self.paths = []
        self.lights = []
        self.vehicles = []

        self.routes = []
        self.vehicle_results = []

        self.nodes_hash_table = {}
        self.paths_hash_table = {}
        self.lights_hash_table = {}
        self.vehicles_hash_table = {}
        self.routes_hash_table = {}

        self.tick = 0
        self.tick_rate = None
        self.tick_time = None
        self.start_time_of_day = None
        self.time_of_day = None

        self.prev_num_cars = 0

    # SAVING AND LOADING DATA

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location, quick_load=quick_load)

        self.update_hash_tables()
        for path in self.paths:
            path.calculate_all(self)

        self.generate_routes()
        self.update_route_hash_table()

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(
            junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_config_file(config_file_location)
        self.set_tick_rate(self.config.tick_rate)
        self.set_start_time_of_day(self.config.start_time_of_day)

    def save_config(self, config_file_location, configuration):
        self.file_manager.save_config_file(config_file_location, configuration)

    def save_results(self, results_file_location):
        self.file_manager.save_results_data_file(results_file_location, self.vehicles)

    def load_results(self, results_file_location):
        self.vehicle_results = self.file_manager.load_results_data_file(results_file_location)

    # HASH TABLE

    def update_hash_tables(self):
        self.update_node_hash_table()
        self.update_path_hash_table()
        self.update_light_hash_table()
        self.update_vehicle_hash_table()

    def update_node_hash_table(self):
        for index, node in enumerate(self.nodes):
            self.nodes_hash_table[str(node.uid)] = index

    def update_path_hash_table(self):
        for index, path in enumerate(self.paths):
            self.paths_hash_table[str(path.uid)] = index

    def update_light_hash_table(self):
        for index, light in enumerate(self.lights):
            self.lights_hash_table[str(light.uid)] = index

    def update_vehicle_hash_table(self):
        for index, vehicle in enumerate(self.vehicles):
            self.vehicles_hash_table[str(vehicle.uid)] = index

    def update_route_hash_table(self):
        for index, route in enumerate(self.routes):
            self.routes_hash_table[str(route.uid)] = index

    # ENVIRONMENT VARIABLES

    def tock(self):
        self.tick += 1

    def set_tick_rate(self, tick_rate: float):
        self.tick_rate = tick_rate
        self.tick_time = 1 / self.tick_rate

    def calculate_seconds_elapsed(self):
        return floor(self.tick / self.tick_rate)

    def calculate_milliseconds_elapsed(self):
        return floor(1000 * self.tick / self.tick_rate)

    def set_start_time_of_day(self, time):
        self.start_time_of_day = time

    def set_time_of_day(self, time):
        self.time_of_day = time

    def calculate_time_of_day(self):
        return self.start_time_of_day.add_milliseconds(self.calculate_milliseconds_elapsed())

    # NODES

    def get_node(self, node_uid) -> Node:
        index = self.nodes_hash_table[str(node_uid)]
        return self.nodes[index]

    def get_node_index(self, node_uid):
        return self.nodes_hash_table[str(node_uid)]

    def set_node(self, node):
        index = self.get_node_index(node.uid)
        self.nodes[index] = node

    def update_node(self, node_uid, x=None, y=None, angle=None):
        index = self.get_node_index(node_uid)
        if x is not None:
            self.nodes[index].x = x
        if y is not None:
            self.nodes[index].y = y
        if angle is not None:
            self.nodes[index].angle = angle

    def add_node(self, x, y, a):
        node_uid = 1
        if len(self.nodes) > 0:
            node_uid = max([node.uid for node in self.nodes]) + 1
        self.nodes.append(Node(node_uid, x, y, a))
        self.nodes_hash_table[str(node_uid)] = len(self.nodes) - 1

    def remove_node(self, node_uid):
        path_uids_to_remove = []
        for path in self.paths:
            if path.start_node_uid == node_uid or path.end_node_uid == node_uid:
                path_uids_to_remove.append(path.uid)

        for path_uid in path_uids_to_remove:
            self.remove_path(path_uid)

        index = self.get_node_index(node_uid)
        self.nodes.pop(index)
        self.update_node_hash_table()
    
    # PATHS

    def get_path(self, path_uid) -> Path:
        index = self.get_path_index(path_uid)
        return self.paths[index]

    def get_path_index(self, path_uid):
        return self.paths_hash_table[str(path_uid)]

    def set_path(self, path):
        index = self.get_path_index(path.uid)
        self.paths[index] = path

    def update_path(self, path_uid, start_node_uid=None, end_node_uid=None, parallel_paths=None):
        index = self.get_path_index(path_uid)
        if start_node_uid is not None:
            self.paths[index].start_node_uid = start_node_uid
        if end_node_uid is not None:
            self.paths[index].end_node_uid = end_node_uid
        if parallel_paths is not None:
            self.paths[index].parallel_paths = parallel_paths

    def add_path(self, start_node_uid, end_node_uid):
        path_uid = 1
        if len(self.paths) > 0:
            path_uid = max([path.uid for path in self.paths]) + 1
        self.paths.append(Path(path_uid, start_node_uid, end_node_uid))
        self.paths_hash_table[str(path_uid)] = len(self.paths) - 1

    def remove_path(self, path_uid):
        index = self.get_path_index(path_uid)
        self.paths.pop(index)
        self.update_path_hash_table()

    # LIGHTS
    
    def get_light(self, light_uid) -> TrafficLight:
        index = self.get_light_index(light_uid)
        return self.lights[index]

    def get_light_index(self, light_uid):
        return self.lights_hash_table[str(light_uid)]

    def get_lights(self) -> List[TrafficLight]:
        return self.lights

    def set_light(self, light):
        index = self.get_light_index(light.uid)
        self.lights[index] = light

    def update_light(self, light_uid, colour=None):
        index = self.get_light_index(light_uid)
        if colour is not None:
            self.lights[index].colour = colour

    def add_light(self, path_uids):
        light_uid = 1
        if len(self.lights) > 0:
            light_uid = max([light.uid for light in self.lights]) + 1
        self.lights.append(TrafficLight(light_uid, path_uids))
        self.lights_hash_table[str(light_uid)] = len(self.lights) - 1

    def remove_light(self, light_uid):
        index = self.get_light_index(light_uid)
        self.lights.pop(index)
        self.update_light_hash_table()

    def get_route(self, route_uid) -> Route:
        index = self.get_route_index(route_uid)
        return self.routes[index]

    def get_route_index(self, route_uid) -> int:
        return self.routes_hash_table[str(route_uid)]

    # VEHICLES
    
    def get_vehicle(self, vehicle_uid) -> Vehicle:
        index = self.get_vehicle_index(vehicle_uid)
        return self.vehicles[index]

    def get_vehicle_index(self, vehicle_uid) -> int:
        return self.vehicles_hash_table[str(vehicle_uid)]

    def get_vehicles(self) -> List[Vehicle]:
        vehicles_uids_to_remove = []
        for vehicle in self.vehicles:
            route = self.get_route(vehicle.get_route_uid())
            path = self.get_path(route.get_path_uid(vehicle.get_path_index()))

            if vehicle.get_route_distance_travelled() >= route.length:
                vehicles_uids_to_remove.append(vehicle.uid)

            if vehicle.get_path_distance_travelled() >= path.get_length():
                vehicle.reset_path_distance_travelled(vehicle.get_path_distance_travelled() - path.get_length())

        for vehicle_uid in vehicles_uids_to_remove:
            self.remove_vehicle(vehicle_uid)

        return self.vehicles

    def get_object_ahead(self, vehicle_uid):
        object_ahead = None

        this_vehicle = self.get_vehicle(vehicle_uid)
        this_route = self.get_route(this_vehicle.get_route_uid())
        this_path = self.get_path(this_route.get_path_uid(this_vehicle.get_path_index()))
        this_vehicle_path_distance_travelled = this_vehicle.get_path_distance_travelled()

        # Search the current path
        min_path_distance_travelled = float('inf')
        for that_vehicle in self.get_vehicles():
            that_path = self.get_path(self.get_route(that_vehicle.get_route_uid()).get_path_uid(that_vehicle.get_path_index()))
            that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()

            if that_path.uid == this_path.uid and min_path_distance_travelled > that_vehicle_path_distance_travelled > this_vehicle_path_distance_travelled:
                min_path_distance_travelled = that_vehicle_path_distance_travelled
                object_ahead = that_vehicle

        if object_ahead is not None:
            return object_ahead, min_path_distance_travelled - this_vehicle_path_distance_travelled

        # Search the paths ahead
        this_route_path_uids = this_route.get_path_uids()
        path_uids_ahead = this_route_path_uids[this_route_path_uids.index(this_path.uid) + 1:]
        distance_travelled_offset = this_path.get_length() - this_vehicle_path_distance_travelled
        for path_uid in path_uids_ahead:
            for light in self.get_lights():
                if light.path_uids[0] == path_uid and not light.allows_traffic():
                    return light, distance_travelled_offset
            for that_vehicle in self.get_vehicles():
                that_path = self.get_path(self.get_route(that_vehicle.get_route_uid()).get_path_uid(that_vehicle.get_path_index()))
                that_vehicle_path_distance_travelled = that_vehicle.get_path_distance_travelled()
                if that_path.uid == path_uid and min_path_distance_travelled > that_vehicle_path_distance_travelled:
                    min_path_distance_travelled = that_vehicle_path_distance_travelled
                    object_ahead = that_vehicle

            if object_ahead is not None:
                return object_ahead, min_path_distance_travelled + distance_travelled_offset
            else:
                distance_travelled_offset += self.get_path(path_uid).get_length()
                continue

        return None, None

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        self.vehicles_hash_table[str(vehicle.uid)] = len(self.vehicles) - 1

    def remove_vehicle(self, vehicle_uid):
        index = self.get_vehicle_index(vehicle_uid)
        self.vehicles.pop(index)
        self.update_vehicle_hash_table()

    # GENERAL
    
    def get_uid_list(self, object_list=None):
        if object_list is None:
            object_list = []

        uid_list = []
        for object in object_list:
            uid_list.append(object.uid)
        return uid_list

    # ROUTES

    def get_route(self, route_uid) -> Path:
        index = self.get_route_index(route_uid)
        return self.routes[index]

    def get_route_index(self, route_uid):
        return self.routes_hash_table[str(route_uid)]

    def set_route(self, route):
        index = self.get_route_index(route.uid)
        self.routes[index] = route

    def calculate_start_nodes(self):
        nodes_uid = self.get_uid_list(self.nodes)
        start_nodes = nodes_uid.copy()
        for path in self.paths:
            if path.end_node_uid in start_nodes:
                start_nodes.remove(path.end_node_uid)
        return start_nodes

    def calculate_end_nodes(self):
        nodes_uid = self.get_uid_list(self.nodes)
        end_nodes = nodes_uid.copy()
        for path in self.paths:
            if path.start_node_uid in end_nodes:
                end_nodes.remove(path.start_node_uid)
        return end_nodes

    def generate_routes(self):
        start_nodes = self.calculate_start_nodes()
        end_nodes = self.calculate_end_nodes()
        self.find_routes(start_nodes, end_nodes)

    def find_routes(self, start_nodes, end_nodes):
        path_sequences = []
        potential_routes = []
        for node in start_nodes:
            paths = self.get_paths_from_start_node(node)
            for path in paths:
                potential_routes.append([path])
        while len(potential_routes):
            to_remove = []
            for route in potential_routes:
                current_route = route.copy()
                new_start_node = (self.get_path(route[-1])).end_node_uid
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
                if (self.get_path(route[-1])).end_node_uid in end_nodes:
                    shorter_path = False
                    for existing_route in path_sequences:
                        if (self.get_path(existing_route[0]).start_node_uid) == (self.get_path(route[0]).start_node_uid) and (self.get_path(existing_route[-1]).end_node_uid) == (self.get_path(route[-1]).end_node_uid):
                            shorter_path = True
                    if shorter_path == False:
                        path_sequences.append(route)
                    to_remove.append(route)
            for route in to_remove:
                potential_routes.remove(route)

        for index, path_sequence in enumerate(path_sequences):
            route_length = sum([self.get_path(path_uid).get_length() for path_uid in path_sequence])
            self.routes.append(Route(index + 1, path_sequence, route_length))

    def get_route_uids(self):
        return [route.uid for route in self.routes]

    def get_paths_from_start_node(self, node_uid):
        paths = []
        for path in self.paths:
            if path.start_node_uid == node_uid:
                paths.append(path.uid)
        return paths

    def get_coordinates_on_path(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        path = self.get_path(self.get_route(vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
        path_distance_travelled = vehicle.get_path_distance_travelled()

        index = floor(path_distance_travelled / path.discrete_length_increment_size)
        return path.discrete_path[index][1], path.discrete_path[index][2]

    def get_curvature(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        path = self.get_path(self.get_route(vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
        path_distance_travelled = vehicle.get_path_distance_travelled()

        index = floor(path_distance_travelled / path.discrete_length_increment_size)
        return path.discrete_path[index][4]

    def get_routes_with_starting_node(self, node_uid):
        routes = []
        for route in self.routes:
            path_uid = route.get_path_uids()[0]
            if self.get_path(path_uid).start_node_uid == node_uid:
                routes.append(route.uid)
        return routes