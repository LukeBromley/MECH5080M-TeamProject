import random
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
import csv
from functools import partial


class Simulation:
    def __init__(self, junction_file_path: str, config_file_path, visualiser_update_function=None):
        self.uid = 0

        # Model
        # TODO: Start at random TOD's
        self.model = Model()
        self.model.load_junction(junction_file_path)
        self.model.generate_routes()
        self.model.load_config(config_file_path)
        self.vehicle_data = []
        self.delays = []
        self.path_backup_total = {}
        self.path_backup = {}
        self.kinetic_energy = {}
        self.kinetic_energy_waste = {}
        self.collision = False
        self.number_of_vehicles_spawned = 0

        # Visualiser
        self.visualiser_update_function = visualiser_update_function

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
            sleep(0.05)

    def compute_single_iteration(self):
        # Spawn vehicles
        for index, node_uid in enumerate(self.model.calculate_start_nodes()):
            nudge_result = self.model.nudge_spawner(node_uid, self.model.calculate_time_of_day())
            if nudge_result is None:
                nudge_result = self.model.nudge_spawn_buffer(node_uid)

            if nudge_result is not None:
                time_created, route_uid, length, width, mass, distance_delta, driver_type = nudge_result
                self.add_vehicle(time_created, route_uid, length, width, mass, distance_delta, driver_type)
                self.number_of_vehicles_spawned += 1

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

        # Calculate Performance Statistics
        # Delay
        self.delays = self.delays + self.model.get_vehicle_delays()

        # Backup
        path_backup_total, path_backup = self.model.get_backed_up_paths(4, 5)

        for path_uid in path_backup_total:
            if str(path_uid) in self.path_backup_total:
                self.path_backup_total[str(path_uid)] += self.model.tick_time
            else:
                self.path_backup_total[str(path_uid)] = self.model.tick_time

        for path_uid in path_backup:
            if path_uid in self.path_backup:
                self.path_backup[path_uid].append(path_backup[path_uid])
            else:
                self.path_backup[path_uid] = [path_backup[path_uid]]

        # Kinetic energy waste
        kinetic_energy, kinetic_energy_waste = self.model.get_vehicle_kinetic_energy_change()

        for vehicle_uid in kinetic_energy:
            if vehicle_uid in self.kinetic_energy:
                self.kinetic_energy[vehicle_uid].append(kinetic_energy[vehicle_uid])
            else:
                self.kinetic_energy[vehicle_uid] = [kinetic_energy[vehicle_uid]]

            if vehicle_uid in self.kinetic_energy_waste:
                self.kinetic_energy_waste[vehicle_uid] += kinetic_energy_waste[vehicle_uid]
            else:
                self.kinetic_energy_waste[vehicle_uid] = kinetic_energy_waste[vehicle_uid]

        # Remove finished vehicles
        self.model.remove_finished_vehicles()

        # Increment Time
        self.model.tock()

    def add_vehicle(self, time_created, route_uid: int, length, width, mass, delta_distance, driver_type):
        self.uid += 1
        initial_speed_multiplier = clamp(delta_distance, 0, 20) / 20
        self.model.add_vehicle(
            Vehicle(
                uid=self.uid,
                start_time=time_created,
                route_uid=route_uid,
                speed=self.model.config.initial_speed * initial_speed_multiplier,
                acceleration=self.model.config.initial_acceleration,
                maximum_acceleration=self.model.config.maximum_acceleration,
                maximum_deceleration=self.model.config.maximum_deceleration,
                maximum_speed=self.model.config.maximum_speed,
                minimum_speed=self.model.config.minimum_speed,
                maximum_lateral_acceleration=self.model.config.maximum_lateral_acceleration,
                preferred_time_gap=self.model.config.autonomous_preferred_time_gap if driver_type == "autonomous" else self.model.config.human_preferred_time_gap,
                length=length,
                width=width,
                mass=mass,
                sensing_radius=self.model.config.maximum_lateral_acceleration,
                min_creep_distance=self.model.config.min_creep_distance,
                driver_type=driver_type
            )
        )


if __name__ == "__main__":
    # Reference Files
    junction_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "junctions", "scale_library_pub_junction.junc")
    configuration_file_path = os.path.join(os.path.dirname(os.path.join(os.path.dirname(os.path.join(os.path.dirname(__file__))))), "configurations", "simulation_config", "cross_road.config")

    # Settings
    scale = 50
    speed_multiplier = 1

    # Visualiser Init
    visualiser = JunctionVisualiser()

    # Simulation
    simulation = Simulation(junction_file_path, configuration_file_path, visualiser.update())

    # Visualiser Setup
    visualiser.define_main(partial(simulation.run_continuous, speed_multiplier))
    visualiser.load_junction(junction_file_path)
    visualiser.set_scale(scale)

    # Run Simulation
    visualiser.open()

