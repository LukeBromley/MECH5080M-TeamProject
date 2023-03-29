from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('./')

from time import sleep
from gui.junction_visualiser import JunctionVisualiser
from library.model import Model
from library.vehicles import Vehicle
from library.maths import calculate_rectangle_corner_coords, calculate_range_overlap, calculate_line_gradient_and_constant, clamp
import os
from functools import partial


class Simulation:
    def __init__(self, junction_file_path: str, config_file_path, visualiser_update_function=None):
        self.uid = 0

        # Model
        self.model = Model()
        self.model.load_junction(junction_file_path)
        self.model.generate_routes()
        self.model.load_config(config_file_path)
        self.delays = []
        self.vehicle_data = []
        self.collision = False

        # Visualiser
        self.visualiser_update_function = visualiser_update_function

        # Highlight Vehicles
        self.highlight_vehicles = []
    
    def get_last_vehicle_uid_spawned(self):
        return self.model.vehicles[-1].uid
    
    def run_continuous(self, speed_multiplier=None):
        for tick in range(self.model.config.simulation_duration):
            self.run_single_iteration()
            if speed_multiplier is not None:
                sleep(self.model.tick_time / speed_multiplier)

    def run_single_iteration(self):
        self.compute_single_iteration()

        # Update visualiser
        if self.visualiser_update_function is not None:
            self.visualiser_update_function(self.vehicle_data, self.model.lights, self.model.calculate_time_of_day(), self.collision)

    def compute_single_iteration(self, lane_change=False):
        # Spawn vehicles
        for index, node_uid in enumerate(self.model.calculate_start_nodes()):
            nudge_result = self.model.nudge_spawner(node_uid, self.model.calculate_time_of_day())
            if nudge_result is not None:
                route_uid, length, width, distance_delta = nudge_result
                self.add_vehicle(node_uid, length, width, distance_delta, lane_change)

        # Remove finished vehicles
        #self.model.remove_finished_vehicles()
        #self.collision = self.model.detect_collisions()

        # Update vehicle position
        self.vehicle_data = []

        self.vehicle_data += self.model.get_ghost_positions(self.model.calculate_time_of_day())

        for vehicle in self.model.vehicles:
            coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
            curvature = self.model.get_vehicle_path_curvature(vehicle.uid)
            angle = self.model.get_vehicle_direction(vehicle.uid)

            object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
            vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead, curvature)
            vehicle.update_position_data([coord_x, coord_y])

            if vehicle.changing_lane:
                self.vehicle_data.append([coord_x, coord_y])
            else:
                if vehicle.uid in self.highlight_vehicles:
                    self.vehicle_data.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, None])
                else:
                    self.vehicle_data.append([coord_x, coord_y, angle, vehicle.length, vehicle.width])

        # Remove finished vehicles
        delays = self.model.remove_finished_vehicles()

        self.delays = self.delays + delays

        # Increment Time
        self.model.tock()

    def add_vehicle(self, node_uid: int, length, width, didstance_delta, lane_change=False):
        self.uid += 1
        initial_speed_multiplier = clamp(didstance_delta, 0, 20) / 20
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.model.calculate_seconds_elapsed(),
                route_uid=self.route_without_lane_change(node_uid) if not lane_change else self.route_with_lane_change(node_uid),
                speed=self.model.config.initial_speed * initial_speed_multiplier,
                acceleration=self.model.config.initial_acceleration,
                maximum_acceleration=self.model.config.maximum_acceleration,
                maximum_deceleration=self.model.config.maximum_deceleration,
                maximum_speed=self.model.config.maximum_speed,
                minimum_speed=self.model.config.minimum_speed,
                maximum_lateral_acceleration=self.model.config.maximum_lateral_acceleration,
                preferred_time_gap=self.model.config.preferred_time_gap,
                length=length,
                width=width,
                sensing_radius=self.model.config.maximum_lateral_acceleration,
                min_creep_distance=self.model.config.min_creep_distance
            )
        )

    def route_with_lane_change(self, start_node_uid):
        start_path_uid = None
        for path in self.model.paths:
            if path.start_node_uid == start_node_uid:
                start_path_uid = path.uid
        for route in self.model.routes:
            if len(route.get_path_uids()) > 1:
                if route.get_path_uids()[0] == start_path_uid:
                    return route.uid

    def route_without_lane_change(self, start_node_uid):
        start_path_uid = None
        for path in self.model.paths:
            if path.start_node_uid == start_node_uid:
                start_path_uid = path.uid
        for route in self.model.routes:
            if len(route.get_path_uids()) == 1:
                if route.get_path_uids()[0] == start_path_uid:
                    return route.uid

    def change_lane(self, vehicle_uid):
        if self.model.is_lane_change_required(vehicle_uid):
            self.model.change_vehicle_lane(vehicle_uid, self.model.calculate_time_of_day())


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "lanes.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations", "cross_road.config")

    # Settings
    scale = 25
    speed_multiplier = 1

    # Visualiser Init
    visualiser = JunctionVisualiser()

    # Simulation
    simulation = Simulation(junction_file_path, configuration_file_path, visualiser.update)

    # Visualiser Setup
    visualiser.define_main(partial(simulation.run_continuous, speed_multiplier))
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

