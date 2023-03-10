from platform import system
if system() == 'Windows':
    import sys
    sys.path.append('../')

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
        self.vehicle_data = []
        self.collision = False

        # Visualiser
        self.visualiser_update_function = visualiser_update_function

        self.freeze_traffic(200)

    def freeze_traffic(self, n: int):
        for light in self.model.lights:
            light.set_red()

        for step in range(n):
            self.compute_single_iteration()

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

    def compute_single_iteration(self):
        # Spawn vehicles
        for index, node_uid in enumerate(self.model.calculate_start_nodes()):
            nudge_result = self.model.nudge_spawner(node_uid, self.model.calculate_time_of_day())
            if nudge_result is not None:
                route_uid, length, width, distance_delta = nudge_result
                self.add_vehicle(route_uid, length, width, distance_delta)

        # Control lights
        for light in self.model.lights:
            light.update(self.model.tick_time)

        # Remove finished vehicles
        self.model.remove_finished_vehicles()

        # Update vehicle position
        self.vehicle_data = []
        for vehicle in self.model.vehicles:
            # TODO: Comment for better performance
            coord_x, coord_y = self.model.get_vehicle_coordinates(vehicle.uid)
            curvature = self.model.get_vehicle_path_curvature(vehicle.uid)
            angle = self.model.get_vehicle_direction(vehicle.uid)

            object_ahead, delta_distance_ahead = self.model.get_object_ahead(vehicle.uid)
            vehicle.update(self.model.tick_time, object_ahead, delta_distance_ahead, curvature)
            vehicle.update_position_data([coord_x, coord_y])
            self.vehicle_data.append([coord_x, coord_y, angle, vehicle.length, vehicle.width, vehicle.uid])

            self.vehicle_data.append([coord_x, coord_y, angle, vehicle.length, vehicle.width])

        # Remove finished vehicles
        self.model.remove_finished_vehicles()

        # Increment Time
        self.model.tock()

    def add_vehicle(self, route_uid: int, length, width, delta_distance):
        self.uid += 1
        initial_speed_multiplier = clamp(delta_distance, 0, 5) / 5
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=self.model.calculate_seconds_elapsed(),
                route_uid=route_uid,
                speed=self.model.config.initial_speed * initial_speed_multiplier,
                acceleration=self.model.config.initial_acceleration,
                maximum_acceleration=self.model.config.maximum_acceleration,
                maximum_deceleration=self.model.config.maximum_deceleration,
                preferred_time_gap=self.model.config.preferred_time_gap,
                maximum_speed=self.model.config.maximum_speed,
                length=length,
                width=width,
                min_creep_distance=self.model.config.min_creep_distance
            )
        )


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "cross_road.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations", "cross_road.config")

    # Settings
    scale = 100
    speed_multiplier = 1

    # Visualiser Init
    visualiser = JunctionVisualiser()

    # Simulation
    simulation = Simulation(junction_file_path, configuration_file_path, visualiser.update)
    simulation.model.setup_fixed_spawning(1)

    # Visualiser Setup
    visualiser.define_main(partial(simulation.run_continuous, speed_multiplier))
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

