from typing import List
from math import floor, sin, cos
import random
from .file_management import FileManagement
from library.infrastructure import Node, Path, TrafficLight, Route
from library.vehicles import Vehicle, GhostVehicle
from library.environment import SpawningRandom, SpawningFixed, SpawningStats
from copy import deepcopy
from library.maths import calculate_magnitude
from shapely.geometry import Polygon


class Model:
    def __init__(self):
        self.file_manager = FileManagement()
        self.config = None

        self.nodes = []
        self.paths = []
        self.lights = []
        self.vehicles = []
        self.ghost_vehicles = []

        self.routes = []
        self.vehicle_results = []

        self.nodes_hash_table = {}
        self.paths_hash_table = {}
        self.lights_hash_table = {}
        self.vehicles_hash_table = {}
        self.routes_hash_table = {}
        self.spawners_hash_table = {}

        self.tick = 0
        self.tick_rate = None
        self.tick_time = None
        self.start_time_of_day = None

        self.spawners = []

        self.prev_num_cars = 0

    # SAVING AND LOADING DATA

    def load_junction(self, junction_file_location, quick_load=False):
        self.nodes, self.paths, self.lights = self.file_manager.load_from_junction_file(junction_file_location, quick_load=quick_load)

        self.update_hash_tables()
        for path in self.paths:
            path.calculate_all(self)
        
        self.update_route_hash_table()

    def save_junction(self, junction_file_location):
        self.file_manager.save_to_junction_file(
            junction_file_location, self.nodes, self.paths, self.lights)

    def load_config(self, config_file_location):
        self.config = self.file_manager.load_sim_config_file(config_file_location)
        self.set_tick_rate(self.config.tick_rate)
        self.set_start_time_of_day(self.config.start_time_of_day)
        if self.config.random_seed is not None:
            self.set_random_seed(self.config.random_seed)
        self.setup_random_spawning(SpawningStats(
            max_spawn_time=self.config.max_spawn_time,
            min_spawn_time=self.config.min_spawn_time,
            mean_spawn_time_per_hour=self.config.mean_spawn_time_per_hour,
            sdev_spawn_time_per_hour=self.config.sdev_spawn_time_per_hour,
            min_spawn_time_per_hour=self.config.min_spawn_time_per_hour,
            distribution_method=self.config.distribution_method,
            max_vehicle_length=self.config.max_vehicle_length,
            min_vehicle_length=self.config.min_vehicle_length,
            max_vehicle_width=self.config.max_vehicle_width,
            min_vehicle_width=self.config.min_vehicle_width,
            mean_vehicle_lengths=self.config.mean_vehicle_lengths,
            mean_vehicle_widths=self.config.mean_vehicle_widths,
            sdev_vehicle_lengths=self.config.sdev_vehicle_lengths,
            sdev_vehicle_widths=self.config.sdev_vehicle_widths
        ))

    def save_config(self, config_file_location, configuration):
        self.file_manager.save_sim_config_file(config_file_location, configuration)

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

    def update_spawner_hash_table(self):
        for index, spawner in enumerate(self.spawners):
            self.spawners_hash_table[str(spawner.node_uid)] = index

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

    def calculate_time_of_day(self):
        return self.start_time_of_day.add_milliseconds(self.calculate_milliseconds_elapsed())

    # SPAWNING

    def get_random_state(self):
        return random.getstate()

    def set_random_state(self, state):
        return random.setstate(state)

    def set_random_seed(self, seed):
        random.seed(seed)

    def setup_random_spawning(self, spawning_stats=None):
        for node_uid in self.calculate_start_nodes():
            self.spawners.append(SpawningRandom(node_uid, self.start_time_of_day, SpawningStats() if spawning_stats is None else spawning_stats))
        self.update_spawner_hash_table()

    def setup_fixed_spawning(self, spawning_time, vehicle_size=(3, 1.8)):
        for node_uid in self.calculate_start_nodes():
            self.spawners.append(SpawningFixed(node_uid, self.start_time_of_day, spawning_time, vehicle_size))
        self.update_spawner_hash_table()

    def nudge_spawner(self, node_uid, time):
        index = self.get_spawner_index(node_uid)
        if self.spawners[index].nudge(time):
            length, width = self.get_spawner_vehicle_size(node_uid)
            distance = self.distance_of_first_vehicle_from_start_node(node_uid)
            if distance > 2 * length:
                route_uid = self.get_spawner_route(node_uid)
                distance_delta = distance - (length/2)
                return route_uid, length, width, distance_delta
        else:
            return None

    def get_spawner_route(self, node_uid):
        index = self.get_spawner_index(node_uid)
        return self.spawners[index].select_route(self.get_routes_with_starting_node(node_uid))

    def get_spawner_vehicle_size(self, node_uid):
        index = self.get_spawner_index(node_uid)
        return self.spawners[index].get_random_vehicle_size()

    def get_spawner_index(self, node_uid):
        return self.spawners_hash_table[str(node_uid)]

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

    def get_paths_from_start_node(self, node_uid):
        paths = []
        for path in self.paths:
            if path.start_node_uid == node_uid:
                paths.append(path.uid)
        return paths

    def get_paths_from_end_node(self, node_uid):
        paths = []
        for path in self.paths:
            if path.end_node_uid == node_uid:
                paths.append(path.uid)
        return paths

    def distance_of_first_vehicle_from_start_node(self, node_uid):
        paths_uids = self.get_paths_from_start_node(node_uid)
        distances = []
        for path_uid in paths_uids:
            distance_ahead = self.distance_of_first_vehicle_from_path_start(path_uid)
            if distance_ahead is None:
                distances.append(float('inf'))
            else:
                distances.append(distance_ahead)
        return min(distances)
    
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

    def distance_of_first_vehicle_from_path_start(self, path_uid):
        this_path = self.get_path(path_uid)

        # Search the current path
        object_ahead = None
        min_path_distance_travelled = float('inf')
        for vehicle in self.vehicles:
            that_path = self.get_path(self.get_route(vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
            that_vehicle_path_distance_travelled = vehicle.get_path_distance_travelled()

            if that_path.uid == this_path.uid and min_path_distance_travelled > that_vehicle_path_distance_travelled > 0:
                min_path_distance_travelled = that_vehicle_path_distance_travelled
                object_ahead = vehicle

        if object_ahead is not None:
            return min_path_distance_travelled - 0
        return None

    def get_vehicles_on_path(self, path_uid):
        vehicle_uids = []
        for vehicle in self.vehicles:
            route = self.get_route(vehicle.get_route_uid())
            if route.get_path_uid(vehicle.get_path_index()) == path_uid:
                vehicle_uids.append(vehicle.uid)
        return vehicle_uids

    # LIGHTS
    
    def get_light(self, light_uid) -> TrafficLight:
        index = self.get_light_index(light_uid)
        return self.lights[index]

    def get_light_index(self, light_uid):
        return self.lights_hash_table[str(light_uid)]

    def set_light(self, light):
        index = self.get_light_index(light.uid)
        self.lights[index] = light

    def set_state(self, light_uid, colour=None):
        index = self.get_light_index(light_uid)
        if colour is not None:
            self.lights[index].set_state(colour)

    def update_light(self, time_delta):
        for light in self.lights:
            light.update(time_delta)

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

    def get_traffic_light_uids(self):
        paths_with_lights = []
        paths_preceding_lights = []
        for light in self.lights:
            light_path = light.path_uids[0]
            paths_with_lights.append(light_path)
            shared_node = self.get_path(light_path).start_node_uid
            preceding_paths = self.get_paths_from_end_node(shared_node)
            for path in preceding_paths:
                paths_preceding_lights.append(path)
        return paths_with_lights, paths_preceding_lights

    # VEHICLES
    
    def get_vehicle(self, vehicle_uid) -> Vehicle:
        index = self.get_vehicle_index(vehicle_uid)
        return self.vehicles[index]

    def get_vehicle_index(self, vehicle_uid) -> int:
        return self.vehicles_hash_table[str(vehicle_uid)]

    def get_vehicle_velocity(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        speed = vehicle.get_speed()
        angle = self.get_angle(vehicle.uid)
        velocity_x = speed * sin(angle)
        velocity_y = speed * cos(angle)
        return velocity_x, velocity_y
    
    def remove_finished_vehicles(self):
        vehicle_uids_to_remove = []
        delays = []
        for vehicle in self.vehicles:
            route = self.get_route(vehicle.get_route_uid())
            path = self.get_path(route.get_path_uid(vehicle.get_path_index()))

            if vehicle.get_path_distance_travelled() >= path.get_length():
                if vehicle.get_path_index() == 0:
                    delays.append(self.get_delay(vehicle.uid))

                # TODO: elif?
                if vehicle.get_path_index() >= len(self.get_route(vehicle.route_uid).get_path_uids())-1:
                    vehicle_uids_to_remove.append(vehicle.uid)
                else:
                    vehicle.increment_path(vehicle.get_path_distance_travelled() - path.get_length())

        for vehicle_uid in vehicle_uids_to_remove:
            self.remove_vehicle(vehicle_uid)
        return delays

    def get_delay(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        time_to_light = self.calculate_seconds_elapsed() - vehicle.start_time
        distance_travelled = vehicle.get_path_distance_travelled()
        max_speed = vehicle.get_max_speed()
        optimal_time = (distance_travelled/max_speed)
        delay = time_to_light - optimal_time
        return delay

    def get_object_ahead(self, vehicle_uid):
        object_ahead = None

        this_vehicle = self.get_vehicle(vehicle_uid)
        this_route = self.get_route(this_vehicle.get_route_uid())
        this_path = self.get_path(this_route.get_path_uid(this_vehicle.get_path_index()))
        this_vehicle_path_distance_travelled = this_vehicle.get_path_distance_travelled()

        # Search the current path
        min_path_distance_travelled = float('inf')
        for that_vehicle in self.vehicles:
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
            for light in self.lights:
                if light.path_uids[0] == path_uid and not light.allows_traffic():
                    return light, distance_travelled_offset
            for that_vehicle in self.vehicles:
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

    def get_vehicle_path_uid(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        route = self.get_route(vehicle.route_uid)
        return route.get_path_uid(vehicle.get_path_index())

    def get_vehicle_next_path_uid(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        route = self.get_route(vehicle.route_uid)
        index = vehicle.get_path_index() + 1
        return route.get_path_uid(index)

    def get_vehicle_coordinates(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        path = self.get_path(self.get_vehicle_path_uid(vehicle_uid))
        path_distance_travelled = vehicle.get_path_distance_travelled()
        index = floor(path_distance_travelled / path.discrete_length_increment_size)
        return path.discrete_path[index][1], path.discrete_path[index][2]

    def get_vehicle_path_curvature(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        path = self.get_path(self.get_route(vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
        path_distance_travelled = vehicle.get_path_distance_travelled()

        index = floor(path_distance_travelled / path.discrete_length_increment_size)
        return path.discrete_path[index][4]

    def get_vehicle_direction(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        path = self.get_path(self.get_route(vehicle.get_route_uid()).get_path_uid(vehicle.get_path_index()))
        path_distance_travelled = vehicle.get_path_distance_travelled()

        index = floor(path_distance_travelled / path.discrete_length_increment_size)
        return path.discrete_path[index][3]

    def is_lane_change_required(self, vehicle_uid):
        vehicle = self.get_vehicle(vehicle_uid)
        route = self.get_route(vehicle.route_uid)
        if (vehicle.get_path_index() < (len(route.get_path_uids())-1)) and (route.get_path_uid(vehicle.get_path_index()+1) in self.get_path(route.get_path_uid(vehicle.get_path_index())).parallel_paths):
            return True
        else:
            return False

    def change_vehicle_lane(self, vehicle_uid, time):
        old_path_uid = self.get_vehicle_path_uid(vehicle_uid)
        old_path = self.get_path(old_path_uid)

        self.ghost_vehicles.append(GhostVehicle(vehicle_uid, old_path_uid, time))

        s = old_path.get_s(self.get_vehicle(vehicle_uid).get_path_distance_travelled())

        new_path_uid = self.get_vehicle_next_path_uid(vehicle_uid)
        new_path = self.get_path(new_path_uid)
        arc_length = new_path.get_arc_length_from_s(s)

        vehicle = self.get_vehicle(vehicle_uid)
        vehicle.increment_path(arc_length)

        vehicle.changing_lane = True

    def get_vehicle_path_length_after_lane_change(self, vehicle_uid):
        old_path_uid = self.get_vehicle_path_uid(vehicle_uid)
        old_path = self.get_path(old_path_uid)
        s = old_path.get_s(self.get_vehicle(vehicle_uid).get_path_distance_travelled())
        new_path_uid = self.get_vehicle_path_uid(vehicle_uid)
        new_path = self.get_path(new_path_uid)
        arc_length = new_path.get_arc_length_from_s(s)
        return arc_length

    def get_ghost_positions(self, time):
        vehicle_data = []

        ghost_vehicle_uids_to_remove = []
        for ghost_vehicle in self.ghost_vehicles:
            t_delta = time.total_milliseconds() - ghost_vehicle.time_created.total_milliseconds()
            if t_delta < ghost_vehicle.change_time:
                vehicle = self.get_vehicle(ghost_vehicle.uid)
                delta_x, delta_y, angle, from_x, from_y = self.calculate_delta_xy_for_ghosts(vehicle, ghost_vehicle)
                x = (t_delta / ghost_vehicle.change_time) * delta_x + from_x
                y = (t_delta / ghost_vehicle.change_time) * delta_y + from_y
                vehicle_data.append([x, y, angle, vehicle.length, vehicle.width, vehicle.uid])
            else:
                ghost_vehicle_uids_to_remove.append(ghost_vehicle.uid)
        
        for ghost_vehicle_uid in ghost_vehicle_uids_to_remove:
            for index, ghost_vehicle in enumerate(self.ghost_vehicles):
                if ghost_vehicle.uid == ghost_vehicle_uid:
                    self.ghost_vehicles.pop(index)
                    vehicle = self.get_vehicle(ghost_vehicle_uid)
                    vehicle.changing_lane = False
                    break

        return vehicle_data
    
    def calculate_delta_xy_for_ghosts(self, vehicle, ghost_vehicle):
        new_path = self.get_path(self.get_vehicle_path_uid(ghost_vehicle.uid))
        s = new_path.get_s(vehicle.get_path_distance_travelled())
        old_path = self.get_path(ghost_vehicle.path_uid)
        from_x, from_y = old_path.get_coordinates_from_s(s)
        to_x, to_y = self.get_vehicle_coordinates(ghost_vehicle.uid)
        angle = self.get_vehicle_direction(ghost_vehicle.uid)
        delta_x = (to_x - from_x)
        delta_y = (to_y - from_y)
        return delta_x, delta_y, angle, from_x, from_y
    
    def detect_nearby_vehicles(self, vehicle_uid):
        nearby_vehicles = []
        vehicle = self.get_vehicle(vehicle_uid)
        own_x, own_y = self.get_vehicle_coordinates(vehicle_uid)
        for other_vehicle in self.vehicles:
            other_x, other_y = self.get_vehicle_coordinates(other_vehicle.uid)
            distance = calculate_magnitude(
                (own_x - other_x), (own_y - other_y))
            minimum_distance = max(vehicle.width, vehicle.length)+max(other_vehicle.width, other_vehicle.length)
            if distance <= minimum_distance and (other_vehicle.uid != vehicle_uid):
                nearby_vehicles.append(other_vehicle)
        return nearby_vehicles

    def detect_collisions(self):
        shapely_vehicles = []
        for vehicle in self.vehicles:
            shapely_vehicles.append(Polygon(self.get_corner_points(vehicle)))

        for v1_index in range(len(shapely_vehicles)):
            for v2_index in range(v1_index + 1, len(shapely_vehicles)):
                if shapely_vehicles[v1_index].intersects(shapely_vehicles[v2_index]):
                    return True
        return False

    def determine_cars_collided(self):
        collisions = []
        for vehicle in self.vehicles:
            nearby_vehicles = self.detect_nearby_vehicles(vehicle.uid)
            v1 = Polygon(self.get_corner_points(vehicle))
            for nearby_vehicle in nearby_vehicles:
                v2 = Polygon(self.get_corner_points(nearby_vehicle))
                if v1.intersects(v2) and [nearby_vehicle, vehicle] not in collisions:
                    collisions.append([vehicle, nearby_vehicle])
        return collisions

    def get_corner_points(self, vehicle):
        angle = self.get_vehicle_direction(vehicle.uid)
        x, y = self.get_vehicle_coordinates(vehicle.uid)
        half_width = vehicle.width/2
        half_length = vehicle.length/2
        c_theta = cos(angle)
        s_theta = sin(angle)
        r1x = -half_length * c_theta - half_width * s_theta
        r1y = -half_length * s_theta + half_width * c_theta
        r2x = half_length * c_theta - half_width * s_theta
        r2y = half_length * s_theta + half_width * c_theta
        return [(x + r1x, y + r1y), (x + r2x, y + r2y), (x - r1x, y - r1y), (x - r2x, y - r2y)]

    # GENERAL
    
    def get_uid_list(self, object_list=None):
        if object_list is None:
            object_list = []

        uid_list = []
        for object in object_list:
            uid_list.append(object.uid)
        return uid_list

    # ROUTES

    def get_route(self, route_uid) -> Route:
        index = self.get_route_index(route_uid)
        return self.routes[index]

    def get_route_index(self, route_uid) -> int:
        return self.routes_hash_table[str(route_uid)]

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
        self.update_route_hash_table()

    def find_routes(self, start_nodes, end_nodes):
        path_sequences = []
        potential_routes = []
        for node in start_nodes:
            paths = self.get_paths_from_start_node(node)
            for path in paths:
                if self.get_path(path).end_node_uid in end_nodes:
                    path_sequences.append([path])
                potential_routes.append([path])
        while len(potential_routes):
            to_remove = []
            for potential_route in potential_routes:
                current_route = deepcopy(potential_route)
                to_remove.append(potential_route)
                new_start_node = (self.get_path(potential_route[-1])).end_node_uid
                following_paths = self.get_paths_from_start_node(new_start_node)
                following_paths += self.get_path(potential_route[-1]).parallel_paths
                for i, path in enumerate(following_paths):
                    if path not in potential_route:
                        new_route = deepcopy(current_route)
                        new_route.append(path)
                        potential_routes.append(new_route)

            for save_route in potential_routes:
                if (self.get_path(save_route[-1])).end_node_uid in end_nodes:   
                    better_path = False
                    for existing_route in path_sequences:
                        if (self.get_path(existing_route[0]).start_node_uid) == (self.get_path(save_route[0]).start_node_uid) and (self.get_path(existing_route[-1]).end_node_uid) == (self.get_path(save_route[-1]).end_node_uid):
                            if len(save_route) > len(existing_route):
                                better_path = True
                    if better_path == False and save_route not in path_sequences:
                        path_sequences.append(save_route)
                    if not (self.get_path(save_route[-1])).parallel_paths:
                        to_remove.append(save_route)
            for remove_route in to_remove:
                if remove_route in potential_routes:
                    potential_routes.remove(remove_route)
        for index, path_sequence in enumerate(path_sequences):
            route_length = sum([self.get_path(path_uid).get_length() for path_uid in path_sequence])
            self.routes.append(Route(index + 1, path_sequence, route_length))

    def get_route_uids(self):
        return [route.uid for route in self.routes]

    def get_routes_with_starting_node(self, node_uid):
        routes = []
        for route in self.routes:
            path_uid = route.get_path_uids()[0]
            if self.get_path(path_uid).start_node_uid == node_uid:
                routes.append(route.uid)
        return routes